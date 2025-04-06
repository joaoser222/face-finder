from fastapi import HTTPException, Depends, APIRouter, UploadFile
from app.utils import get_current_user
from app.models.user import User
from typing import Any
from app.models.file import File
import os
from tortoise import transactions

class BaseController:
    model = None
    prefix = ""
    current_user = None  # Atributo para armazenar o usuário autenticado

    def __init__(self):
        # Cria o router com o prefixo dinâmico
        self.router = APIRouter(prefix=f"/{self.prefix}", tags=[self.prefix])

        # Adiciona uma dependência global para o roteador
        self.router.dependencies.append(Depends(self.set_current_user))

        # Define as rotas
        self.router.add_api_route("/list", self.get_all, methods=["GET"])
        self.router.add_api_route("/show/{id}", self.show, methods=["GET"])
        self.router.add_api_route("/create", self.create, methods=["POST"])
        self.router.add_api_route("/update/{id}", self.update, methods=["PUT"])
        self.router.add_api_route("/delete/{id}", self.delete, methods=["DELETE"])

    async def set_current_user(self, user: User = Depends(get_current_user)):
        # Armazena o usuário autenticado no atributo da classe
        self.current_user = user

    async def get_all(self):
        try:
            return await self.model.all()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def show(self, id: int):
        try:
            record = await self.model.get_or_none(id=id)
            if not record:
                raise HTTPException(status_code=404, detail="Registro não encontrado")
            return record
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create(self, params: dict):
        async with transactions.in_transaction() as transaction:
            try:
                params["user_id"] = self.current_user.id
                record = await self.model.create(**params)
                return record
            except Exception as e:
                await transaction.rollback()
                raise HTTPException(status_code=400, detail=str(e))
    
    async def update(self, id: int, params: dict):
        async with transactions.in_transaction() as transaction:
            try:
                params["user_id"] = self.current_user.id
                record = await self.model.get_or_none(id=id)
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                await record.update(**params)
                return record
            except Exception as e:
                await transaction.rollback()
                raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, id: int):
        async with transactions.in_transaction() as transaction:
            try:
                record = await self.model.get_or_none(id=id)
                if not record:
                    raise HTTPException(status_code=404, detail="Registro não encontrado")
                await record.delete()
                return {"message": "Registro deletado com sucesso"}
            except Exception as e:
                await transaction.rollback()
                raise HTTPException(status_code=400, detail=str(e))
    
