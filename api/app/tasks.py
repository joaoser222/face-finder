from celery import Celery
import os
import zipfile
from app.models.archive import Archive
from app.models.photo import Photo
from app.models.collection import Collection, CollectionStatus
from app.models.job import Job, JobStatus
from app.utils import logger_info, logger_error
import shutil
import asyncio
from app.config import init_db, close_db
import redis
from concurrent.futures import ThreadPoolExecutor
from app.services.recognition import Recognition

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

async def wrap_db_ctx(func, *args, **kwargs):
    try:
        await init_db()
        result = await func(*args, **kwargs)
        return result
    except Exception as e:
        logger_error(__name__, e)
        raise
    finally:
        await close_db()

def async_to_sync(func, *args, **kwargs) -> None:
    asyncio.run(wrap_db_ctx(func, *args, **kwargs))

def check_job(job_id):
    job = Job.get_or_none(id=job_id)
    if not job:
        raise Exception("Job não encontrado")
    return job

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def check_downloaded_model(self):
    """
    Verifica se o modelo de reconhecimento foi baixado
    """
    try:
        async def __action__():
            try:
                task = None
                if not Recognition.is_model_downloaded():
                    task = await Job.create(
                        process_type="download_recognition_model",
                        owner_type="system",
                        owner_id=1
                    )
                    await Recognition.download_model()
                    await task.delete()
            except Exception as e:
                logger_error(__name__, e)
                if task:
                    task.status = JobStatus.FAILED
                    await task.save()
                raise
        
        async_to_sync(__action__)
    except Exception as e:
        self.retry(exc=e)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
async def collection_uncompression(self, job_id):
    """
    Descompacta um arquivo e move as imagens para o diretório de imagens da coleção.
    """
    try:
        job = check_job(job_id)
        temp_dir = f'/app/files/temp/{job.owner_id}'
        archive = await Archive.get_or_none(id=job.owner_id)
        if not archive:
            raise Exception("Arquivo não encontrado")
        
        collection = await Collection.get_or_none(id=archive.owner_id)
        if not collection:
            raise Exception("Coleção não encontrada")

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
            if not collection.thumbnail_photo:
                collection.thumbnail_photo = photo
            
            shutil.move(item.path, photo.file_path)
            added_photos_counter += 1

        # Atualiza coleção
        collection.status = CollectionStatus.INDEXING
        collection.photo_quantity = added_photos_counter
        await collection.save()

        # Cria novo job para indexação
        indexation_job = await Job.create(
            process_type="collection_indexation",
            owner_type="collection",
            owner_id=collection.id
        )

        collection_indexation.delay(indexation_job.id)

        # Limpeza final
        os.remove(archive.file_path)
        await archive.delete()
        shutil.rmtree(temp_dir)
        await job.delete()

        logger_info(__name__, f'{added_photos_counter} foto(s) adicionada(s) à coleção {collection.id}')

    except Exception as e:
        logger_error(__name__, e)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
async def collection_indexation(self, job_id):
    """
    Indexa as imagens de uma coleção usando processamento paralelo
    """
    try:
        job = check_job(job_id)
        collection = await Collection.get_or_none(id=job.owner_id)

        if not collection:
            await job.delete()
            logger_info(__name__, f'Coleção {job.owner_id} não encontrada')
            return
        
        # Obtém todas as fotos da coleção
        photos = await Photo.filter(
            owner_id=collection.id,
            owner_type="collection",
            is_indexed=False
        ).all()
        
        # Inicializa o FaceAnalysis uma única vez (será reutilizado nas threads)
        recognition = await Recognition.create()

        # Configuração do ThreadPool
        max_workers = min(4, len(photos))  # Limita a 4 threads ou menos se tiver poucas fotos
        loop = asyncio.get_running_loop()
        
        # Processa as fotos em paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = []
            for photo in photos:
                # Submete cada foto para processamento no thread pool
                task = loop.run_in_executor(
                    executor,
                    lambda p=photo: asyncio.run_coroutine_threadsafe(
                        recognition.process_single_photo(p),
                        loop
                    ).result()
                )
                tasks.append(task)
            
            # Aguarda a conclusão de todas as tarefas
            await asyncio.gather(*tasks)
        
        # Atualiza coleção para "concluído"
        collection.status = CollectionStatus.FINISHED
        await collection.save()
        
        await job.delete()
        logger_info(__name__, f'Imagens da coleção {collection.id} indexadas com sucesso')
        
    except Exception as e:
        logger_error(__name__,e)
        raise
