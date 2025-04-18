from fastapi import HTTPException, Depends, UploadFile,Query
from fastapi.responses import JSONResponse
from app.utils import logger_info,logger_error
from typing import Any
import os
from tortoise import transactions,connections
import shutil
from .base_controller import BaseController

class ViewController(BaseController):
    model = None
    prefix = ""
    current_user = None  # Atributo para armazenar o usuário autenticado
    search_field = "name"

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
    
    async def query_paginator(self,raw_query: str,page: int = 1,per_page: int = 24) -> dict:
        """
        Realiza a paginação de uma raw SQL query usando Tortoise-ORM.
        
        Args:
            raw_query: Query SQL bruta (sem LIMIT/OFFSET)
            page: Número da página desejada (começa em 1)
            per_page: Quantidade de itens por página
        Returns:
            dict: Objeto com os resultados paginados e metadados
        """
        try:
            # Calcular offset
            offset = (page - 1) * per_page
            
            # Obter conexão do banco de dados
            conn = connections.get("default")

            # Query para contar o total de registros
            count_query = f"SELECT COUNT(id) FROM ({raw_query}) AS total"
            
            # Executar contagem total
            total = await conn.execute_query_dict(count_query)
            total = total[0]["count"] if total else 0

            # Calcular total de páginas
            total_pages = (total + per_page - 1) // per_page

            # Aplicar paginação na query principal
            paginated_query = f"{raw_query} LIMIT {per_page} OFFSET {offset}"
            items = await conn.execute_query_dict(paginated_query)

            return {
                "data": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages
            }
        except Exception as e:
            logger_error(__name__,e)
            raise


    async def get_all(self,search: str = Query(''),page: int = Query(1, ge=1)):
        """
        Retorna todos os registros da model
        """
        try:
            query = self.get_model_by_user()
            if self.search_field:
                query = query.filter(**{f"{self.search_field}__icontains": search})
            
            return await self.query_paginator(query.sql(True), page)
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
        try:
            async with transactions.in_transaction():
                params["user_id"] = self.current_user.id
                record = await self.model.create(**params)
            return record
        except Exception as e:
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
        try:
            async with transactions.in_transaction():
                record = await self.get_model_by_user().get_or_none(id=id)
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                await record.apply_update(**params)
            return record
        except Exception as e:
            logger_error(__name__,e)
            raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, id: int):
        """
        Exclui um registro na model pelo id

        Args:
            id (int): Id do registro
        """
        try:
            async with transactions.in_transaction():
                record = await self.get_model_by_user().get_or_none(id=id)
                model_name = record.__class__.__name__.lower()
                model_folder = f"/app/files/{model_name}/{record.id}"
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                
                # Remove todos os arquivos do diretório local caso existam
                if os.path.exists(model_folder):
                    shutil.rmtree(model_folder)

                await record.delete()
            return JSONResponse(content={})
        except Exception as e:
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
        try:
            async with transactions.in_transaction():
                file_record = await file_model.create_file(owner, file.filename,file.size)

                # Cria a estrutura de diretórios se não existir
                directory = os.path.dirname(file_record.file_path)
                os.makedirs(directory, exist_ok=True)

                # Salva o arquivo na pasta local
                with open(file_record.file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
            return file_record
        except Exception as e:
            logger_error(__name__,e)
            raise
