from typing import List
from fastapi import HTTPException
from fastapi import APIRouter

class BaseController:
    model = None
    prefix = ""

    def __init__(self):
        # Cria o router com o prefixo dinâmico
        self.router = APIRouter(prefix=f"/{self.prefix}", tags=[self.prefix])

        # Define as rotas
        self.router.add_api_route("/list", self.get_all, methods=["GET"])
        self.router.add_api_route("/show/{id}", self.show, methods=["GET"])
        self.router.add_api_route("/create", self.create, methods=["POST"])
        self.router.add_api_route("/delete/{id}", self.delete, methods=["DELETE"])

    async def get_all(self):
        return await self.model.all()

    async def show(self, id: int):
        record = await self.model.get_or_none(id=id)
        if not record:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return record

    async def create(self, params: dict):
        try:
            record = await self.model.create(**params)
            return record
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, id: int):
        record = await self.model.get_or_none(id=id)
        if not record:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        await record.delete()
        return {"message": "Registro deletado com sucesso"}