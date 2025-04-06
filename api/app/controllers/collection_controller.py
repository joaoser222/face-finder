from fastapi import UploadFile, File, Form,HTTPException
from typing import Optional
import json
from app.models.collection import Collection
from app.models.file import File
from app.models.queue import Queue
from tortoise import transactions
from .base_controller import BaseController

class CollectionController(BaseController):
    model = Collection
    prefix = "collections"

    async def create(
        self,
        file: UploadFile,
        params: str = Form(...)
    ):
        async with transactions.in_transaction() as transaction:
            try:
                # Converte a string JSON para dicionário
                params_dict = json.loads(params)
                params_dict["user_id"] = self.current_user.id

                record = await self.model.create(**params_dict)

                # Processa o arquivo dentro da mesma transaction
                file_record = await self.process_uploaded_file(file, record)
                
                # Cria a queue de descompactação
                queue = await Queue.create(
                    user_id=self.current_user.id,
                    process_type="uncompression",
                    owner_type=file_record.__class__.__name__,
                    owner_id=file_record.id
                )

                return record

            except json.JSONDecodeError:
                await transaction.rollback()
                raise HTTPException(400, "Parâmetros inválidos (não é JSON válido)")
            except Exception as e:
                await transaction.rollback()
                raise HTTPException(400, str(e))
    
    async def update(
        self,
        id: int,
        file: Optional[UploadFile],
        params: str = Form(...)
    ):
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
                    file_record = await self.process_uploaded_file(file, record)
                    
                    # Cria a queue de descompactação
                    queue = await Queue.create(
                        user_id=self.current_user.id,
                        process_type="uncompression",
                        owner_type=file_record.__class__.__name__,
                        owner_id=file_record.id
                    )

                return record

            except json.JSONDecodeError:
                await transaction.rollback()
                raise HTTPException(400, "Parâmetros inválidos (não é JSON válido)")
            except Exception as e:
                await transaction.rollback()
                raise HTTPException(400, str(e))