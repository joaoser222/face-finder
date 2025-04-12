from celery import Celery
import time
import os
import zipfile
from app.models.archive import Archive
from app.models.photo import Photo
from app.models.collection import Collection
from app.models.queue import Queue
from app.utils import logger_info, logger_error
import shutil
import asyncio
from app.config import init_db, close_db
import redis
from tortoise.transactions import in_transaction

# Configuração do Redis
redis_client = redis.from_url(os.getenv("DATABASE_REDIS_URL"))

# Configuração do Celery
celery_app = Celery(
    "facefinder",
    broker=os.getenv("DATABASE_REDIS_URL"), 
    backend=os.getenv("DATABASE_REDIS_URL"),
)

# Configurações adicionais do Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

# Configurações do Beat (agendador)
celery_app.conf.beat_schedule = {
    'periodic_check': {
        'task': 'app.tasks.periodic_check',
        'schedule': 60.0,  # A cada 1 minuto
        'options': {'queue': 'periodic'}  # Envia para fila específica
    },
}

async def wrap_db_ctx(func, *args, **kwargs) -> None:
    try:
        await init_db()
        await func(*args, **kwargs)
    except Exception as e:
        logger_error(__name__, f"Erro no contexto do DB: {str(e)}")
        raise
    finally:
        await close_db()

def async_to_sync(func, *args, **kwargs) -> None:
    asyncio.run(wrap_db_ctx(func, *args, **kwargs))

async def process_queue(queue_id=None):
    """
    Processa uma queue
    Args:
        queue_id (int,optional): ID da queue
    """
    try:
        async with in_transaction():
            if(queue_id is None):
                queue = await Queue.filter(status=0).limit(1).select_for_update().get()
            else:
                queue = await Queue.select_for_update().get_or_none(id=queue_id)

            if not queue:
                raise Exception("Queue não encontrada")
        
            # Atualiza status para "processando"
            queue.status = 1
            await queue.save()
            
            task_func = globals().get(queue.process_type)
            if not task_func:
                raise Exception(f"Tipo de processo inválido: {queue.process_type}")
            
            await task_func(queue)
            
            # Atualiza status para "concluído"
            queue.status = 2
            await queue.save()
    except Exception as e:
        queue.status = -1
        await queue.save()
        logger_error(__name__, f"Erro ao processar queue {queue_id}: {str(e)}")
        raise

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_queue(self, queue_id):
    try:
        async_to_sync(process_queue, queue_id)
        
    except Exception as exc:
        logger_error(__name__, f"Erro ao processar queue {queue_id}: {str(exc)}")
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            async_to_sync(
                lambda: Queue.filter(id=queue_id).update(status=-1, error_message=str(exc))
            )
        raise


@celery_app.task
def periodic_check():
    """Verificação periódica a cada minuto"""
    try:
        async_to_sync(process_queue)
    except Exception as e:
        logger_error(__name__, f"Erro na verificação periódica: {str(e)}")

async def collection_uncompression(queue):
    """
    Descompacta um arquivo e move as imagens para o diretório de imagens da coleção.
    """
    temp_dir = f'/app/files/temp/{queue.owner_id}'
    try:
        async with in_transaction():
            archive = await Archive.get_or_none(id=queue.owner_id).select_related('owner')
            if not archive or not archive.owner:
                raise Exception("Arquivo ou coleção não encontrada")
            
            collection = archive.owner
            os.makedirs(temp_dir, exist_ok=True)
            added_photos_counter = 0

            with zipfile.ZipFile(archive.file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            for item in os.scandir(temp_dir):
                if not item.is_file():
                    continue
                    
                _, ext = os.path.splitext(item.name.lower())
                if ext not in ['.jpg', '.jpeg', '.png']:
                    os.remove(item.path)
                    continue
                
                # Processa cada foto
                photo = await Photo.create_file(collection, item.name, item.stat().st_size)
                if not collection.thumbnail_file:
                    collection.thumbnail_file = photo
                
                shutil.move(item.path, photo.file_path)
                added_photos_counter += 1

            # Atualiza coleção
            collection.status = 1
            collection.photo_quantity = added_photos_counter
            await collection.save()

            # Cria nova queue para indexação
            await Queue.create(
                user_id=queue.user_id,
                process_type="collection_indexation",
                owner_type="Collection",
                owner_id=collection.id
            )

            # Limpeza final
            os.remove(archive.file_path)
            await archive.delete()
            shutil.rmtree(temp_dir)
            await queue.delete()

            logger_info(__name__, f'{added_photos_counter} foto(s) adicionada(s) à coleção {collection.id}')

    except Exception as e:
        logger_error(__name__, f"Erro ao descompactar: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise