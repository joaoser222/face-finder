from app.models.user import User
from typing import List
from fastapi import HTTPException

class UserController:
    @staticmethod
    async def create_user(username: str, email: str):
        try:
            user = await User.create_user(username=username, email=email)
            return user
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def get_all_users() -> List[User]:
        return await User.all()

    @staticmethod
    async def get_user_by_id(user_id: int):
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return user

    @staticmethod
    async def delete_user(user_id: int):
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        await user.delete()
        return {"message": "Usuário deletado com sucesso"} 