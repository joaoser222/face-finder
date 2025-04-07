from celery import Celery
import time
import os,zipfile
from app.models.file import File
from app.models.collection import Collection
from app.utils import logger
import shutil

class Task:
    @staticmethod
    def uncompression(queue):
        """
        Descompacta um arquivo zip e move as imagens para o diretório de imagens da coleção.
        """
        try:
            file = File.get_or_none(id=queue.owner_id)
            collection = Collection.get_or_none(id=file.owner_id)
            if not file:
                raise Exception("Arquivo não encontrado")
            else:
                # Cria a estrutura de diretórios se não existir
                directory = os.path.dirname(f'/app/files/temp/{file.id}')
                os.makedirs(directory, exist_ok=True)

                # Extrai todos os arquivos do zip na pasta temporária
                zip_ref = zipfile.ZipFile(file.file_path, 'r')
                zip_ref.extractall(directory)
                zip_ref.close()
                added_photos_counter = 0
                items = os.scandir(directory)

                # Percorre todos os arquivos do diretório
                for item in items:
                    if item.is_file():
                        _,ext = os.path.splitext(item.name)

                        # Caso o arquivo seja uma imagem, move para o diretório de imagens. 
                        # Caso contrário, remove o arquivo
                        if (ext.lower() in ['.jpg', '.jpeg', '.png']):
                            photo = File.create_file(collection, item.name, item.stat().st_size)
                            shutil.move(item.path, photo.file_path)
                            added_photos_counter += 1
                        else:
                            os.remove(item.path)
                
                # Remove o arquivo zip original
                os.remove(file.file_path)
                
                # Remove a pasta temporária
                shutil.rmtree(directory)
                
                # Remove a queue
                queue.delete()

                if(added_photos_counter > 0):
                    # Atualiza o status da collection
                    collection.status = 1
                    collection.photo_count = added_photos_counter
                    collection.save()
                    logger().info(f'{added_photos_counter} Foto(s) adicionada(s) na coleção {collection.id}')
                else:
                    logger().info(f'Nenhuma foto adicionada na coleção {collection.id}')
                
        except Exception as e:
            logger().error(str(e))
            queue.status = -1
            queue.save()
            
# Configuração do Celery
celery_app = Celery(
    "facefinder",
    broker=os.getenv("DATABASE_REDIS_URL"), 
    backend=os.getenv("DATABASE_REDIS_URL"),
)

@celery_app.task
def queue_process(queue_id):
    try:
        queue = Queue.get_or_none(id=queue_id)
        if not queue:
            raise Exception("Queue não encontrada")
        task_func = getattr(Task,queue.process_type)
        task_func(queue)
    except Exception as e:
        logger().error(str(e))

    
