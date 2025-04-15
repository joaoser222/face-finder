from fastapi import HTTPException, Depends, UploadFile,Query
from fastapi.responses import JSONResponse
from app.utils import logger_info,logger_error
from typing import Any
import os
from tortoise import transactions
import shutil
from .base_controller import BaseController

class ViewController(BaseController):
    model = None
    prefix = ""
    current_user = None  # Atributo para armazenar o usuário autenticado
    search_field = ""

    def __init__(self):
        super().__init__()
        
        # Define as rotas
        self.router.add_api_route("/list", self.get_all, methods=["GET"], dependencies=[Depends(self.set_current_user)])
        self.router.add_api_route("/show/{id}", self.show, methods=["GET"], dependencies=[Depends(self.set_current_user)])
        self.router.add_api_route("/create", self.create, methods=["POST"], dependencies=[Depends(self.set_current_user)])
        self.router.add_api_route("/update/{id}", self.update, methods=["PUT"], dependencies=[Depends(self.set_current_user)])
        self.router.add_api_route("/delete/{id}", self.delete, methods=["DELETE"], dependencies=[Depends(self.set_current_user)])
    
    def get_model_by_user(self):
        """
        Filtra os registros da model pelo usuário autenticado
        """
        return self.model.filter(user_id=self.current_user.id)
    
    async def query_paginator(self, query, page):
        """
        Retorna os registros da model com paginação
        """
        try:
            per_page = 24
            total = await query.count()
            items = await query.offset((page - 1) * per_page).limit(per_page)
            
            return {
                "data": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            }
        except Exception as e:
            logger_error(__name__,e)
            raise


    async def get_all(self,search: str = Query(None),page: int = Query(1, ge=1)):
        """
        Retorna todos os registros da model
        """
        try:
            query = self.get_model_by_user()
            if self.search_field:
                query = query.filter(**{f"{self.search_field}__icontains": search})
            
            return await self.query_paginator(query, page)
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
            record = await self.get_model_by_user().get_or_none(id=id)
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
                record = await self.get_model_by_user().get_or_none(id=id)
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
                record = await self.get_model_by_user().get_or_none(id=id)
                model_name = record.__class__.__name__.lower()
                model_folder = f"/app/files/{model_name}/{record.id}"
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                
                # Remove todos os arquivos do diretório local
                if os.path.exists(model_folder):
                    shutil.rmtree(model_folder)

                await record.delete()
                return JSONResponse(content={})
            except Exception as e:
                await transaction.rollback()
                logger_error(__name__,e)
                raise HTTPException(400, str(e))
    
    async def process_uploaded_file(self, file: UploadFile,file_model: Any, owner: Any):
        """
        Processa o arquivo e retorna o registro do arquivo processado

        Args:
            file (UploadFile): Arquivo enviado pelo usuário
            owner (Any): Entidade proprietária do arquivo
        Returns:
            FileModel: Arquivo processado
        """
        async with transactions.in_transaction() as transaction:
            try:
                file_record = await file_model.create_file(owner, file.filename,file.size)

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
