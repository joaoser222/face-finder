from fastapi import UploadFile, Form,HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import json
from app.models.collection import Collection
from app.models.queue import Queue
from app.models.archive import Archive
from tortoise import transactions
from .view_controller import ViewController
from app.tasks import send_queue
from app.utils import logger_info,logger_error
from fastapi import Query

class CollectionController(ViewController):
    model = Collection
    prefix = "collections"
    
    async def __process_compressed_file(self, file: UploadFile, record):
        """
        Processa o arquivo compactado

        Args:
            file (UploadFile): Arquivo compactado enviado pelo usuário
            record (Collection): Registro da collection
        """
        try:
            file_record = await self.process_uploaded_file(file, Archive,record)
            
            # Cria a queue de descompactação
            queue = await Queue.create(
                user_id=self.current_user.id,
                process_type="collection_uncompression",
                owner_type=file_record.__class__.__name__,
                owner_id=file_record.id
            )

            logger_info(__name__,f"Queue criada para descompactação: {queue.id}")

            send_queue.delay(queue.id)
        except Exception as e:
            logger_error(__name__,e)
            raise

    async def create(
        self,
        file: UploadFile,
        params: str = Form(...)
    ):
        """
        Cria um novo registro de collection

        Args:
            file (UploadFile): Arquivo compactado enviado pelo usuário
            params (str): Parâmetros do registro
        Returns:
            Collection: Registro criado
        """
        async with transactions.in_transaction() as transaction:
            try:
                # Converte a string JSON para dicionário
                params_dict = json.loads(params)
                params_dict["user_id"] = self.current_user.id

                record = await self.model.create(**params_dict)

                # Processa o arquivo
                await self.__process_compressed_file(file, record)
                
                return record

            except json.JSONDecodeError as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, str(e))
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, str(e))
    
    async def update(
        self,
        id: int,
        file: Optional[UploadFile],
        params: str = Form(...)
    ):
        """
        Atualiza um registro de collection pelo id

        Args:
            id (int): Id do registro
            file (UploadFile,optional): Arquivo compactado enviado pelo usuário
            params (str): Parâmetros do registro
        Returns:
            Collection: Registro atualizado
        """
        async with transactions.in_transaction() as transaction:
            try:
                # Converte a string JSON para dicionário
                params_dict = json.loads(params)
                params_dict["user_id"] = self.current_user.id

                record = await self.model.get_or_none(id=id)
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                await record.update(**params_dict)

                # Caso exista um novo arquivo na atualização, processa o arquivo
                if file:
                    await self.__process_compressed_file(file, record)

                return record

            except json.JSONDecodeError as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, "Parâmetros inválidos (não é JSON válido)")
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, str(e))