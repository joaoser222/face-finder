from app.models.search import Search
from .view_controller import ViewController
from app.models.photo import Photo
from app.models.queue import Queue
from tortoise import transactions
from fastapi import UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import json
from app.utils import logger_info,logger_error

class SearchController(ViewController):
    model = Search
    prefix = "searches"

    async def create(
        self,
        file: UploadFile,
        params: str = Form(...)
    ):
        """
        Cria um novo registro de pesquisa

        Args:
            file (UploadFile): Arquivo de imagem para pesquisa enviado pelo usuário
            params (str): Parâmetros do registro
        Returns:
            Search: Registro criado
        """
        async with transactions.in_transaction() as transaction:
            try:
                # Converte a string JSON para dicionário
                params_dict = json.loads(params)
                params_dict["user_id"] = self.current_user.id

                record = await self.model.create(**params_dict)

                # Processa o arquivo
                file_record = await self.process_uploaded_file(file, Photo,record)
            
                # Cria a queue de processamento
                queue = await Queue.create(
                    user_id=self.current_user.id,
                    process_type="search_collection",
                    owner_type=record.__class__.__name__,
                    owner_id=record.id
                )

                logger_info(__name__,f"Queue criada para processamento de pesquisa: {queue.id}")
                
                return record

            except json.JSONDecodeError as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, str(e))
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, str(e))