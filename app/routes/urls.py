from fastapi import APIRouter
from app.controllers.user_controller import UserController

# Criando o router principal
main_router = APIRouter()

# Rotas de usuário
@main_router.post("/users/")
async def create_user(username: str, email: str):
    return await UserController.create_user(username=username, email=email)

@main_router.get("/users/")
async def get_users():
    return await UserController.get_all_users()

@main_router.get("/users/{user_id}")
async def get_user(user_id: int):
    return await UserController.get_user_by_id(user_id)

@main_router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return await UserController.delete_user(user_id) 