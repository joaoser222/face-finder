from fastapi import HTTPException, Depends, UploadFile
from fastapi.responses import JSONResponse
from app.utils import logger_info,logger_error
from typing import Any
from app.models.file import File
import os
from tortoise import transactions
import shutil
from .base_controller import BaseController

class ViewController(BaseController):
    model = None
    prefix = ""
    current_user = None  # Atributo para armazenar o usuário autenticado

    def __init__(self):
        super().__init__()

        # Adiciona uma dependência global para o roteador
        self.router.dependencies.append(Depends(self.set_current_user))

        # Define as rotas
        self.router.add_api_route("/list", self.get_all, methods=["GET"])
        self.router.add_api_route("/show/{id}", self.show, methods=["GET"])
        self.router.add_api_route("/create", self.create, methods=["POST"])
        self.router.add_api_route("/update/{id}", self.update, methods=["PUT"])
        self.router.add_api_route("/delete/{id}", self.delete, methods=["DELETE"])
    
    def __get_model_by_user(self):
        """
        Filtra os registros da model pelo usuário autenticado
        """
        return self.model.filter(user_id=self.current_user.id)

    async def get_all(self):
        """
        Retorna todos os registros da model
        """
        try:
            return await self.__get_model_by_user().all()
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))

    async def show(self, id: int):
        """
        Retorna um registro da model pelo id

        Args:
            id (int): Id do registro
        Returns:
            Record: Registro encontrado
        """
        try:
            record = await self.model.filter(user_id=self.current_user.id).get_or_none(id=id)
            if not record:
                raise HTTPException(status_code=404, detail="Registro não encontrado")
            return record
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))

    async def create(self, params: dict):
        """
        Cria um novo registro na model

        Args:
            params (dict): Parâmetros do registro
        Returns:
            Record: Registro criado
        """
        async with transactions.in_transaction() as transaction:
            try:
                params["user_id"] = self.current_user.id
                record = await self.model.create(**params)
                return record
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(status_code=400, detail=str(e))
    
    async def update(self, id: int, params: dict):
        """
        Atualiza um registro na model pelo id

        Args:
            id (int): Id do registro
            params (dict): Parâmetros do registro
        Returns:
            Record: Registro atualizado
        """
        async with transactions.in_transaction() as transaction:
            try:
                record = await self.__get_model_by_user().get_or_none(id=id)
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                await record.update(**params)
                return record
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, id: int):
        """
        Exclui um registro na model pelo id

        Args:
            id (int): Id do registro
        """
        async with transactions.in_transaction() as transaction:
            try:
                record = await self.__get_model_by_user().get_or_none(id=id)
                model_name = record.__class__.__name__.lower()
                model_folder = f"/app/files/{model_name}/{record.id}"
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                
                # Remove todos os arquivos do diretório local
                if os.path.exists(model_folder):
                    shutil.rmtree(model_folder)
                
                # Remove todos os arquivos do banco de dados
                await File.filter(owner_type=model_name, owner_id=record.id).delete()

                await record.delete()
                return JSONResponse(content={})
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, str(e))
    
    async def process_uploaded_file(self, file: UploadFile, owner: Any):
        """
        Processa o arquivo e retorna o registro do arquivo processado

        Args:
            file (UploadFile): Arquivo enviado pelo usuário
            owner (Any): Entidade proprietária do arquivo
        Returns:
            File: Arquivo processado
        """
        async with transactions.in_transaction() as transaction:
            try:
                file_record = await File.create_file(owner, file.filename,file.size)

                # Cria a estrutura de diretórios se não existir
                directory = os.path.dirname(file_record.file_path)
                os.makedirs(directory, exist_ok=True)

                # Salva o arquivo na pasta local
                with open(file_record.file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                return file_record
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise
