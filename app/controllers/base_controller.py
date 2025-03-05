from typing import List
from fastapi import HTTPException
from fastapi import APIRouter

class BaseController:
    model = None
    router = APIRouter()
    endpoint = ''

    @router.post("/")
    async def create(self, params: dict):
        try:
            record = await self.model.create(**params)
            return record
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get(f"/{endpoint}")
    async def get_all(self):
        return await self.model.all()

    @router.get(f"/{endpoint}/{id}")
    async def get_by_id(self,id: int):
        record = await self.model.get_or_none(id=id)
        if not record:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return record

    @router.delete(f"/{endpoint}/{id}")
    async def delete(self,id: int):
        record = await self.model.get_or_none(id=id)
        if not record:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        await record.delete()
        return {"message": "Registro deletado com sucesso"} 