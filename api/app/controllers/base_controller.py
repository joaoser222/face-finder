from fastapi import Depends, APIRouter
from app.utils import get_current_user
from app.models.user import User

class BaseController:
    prefix = ""
    current_user = None  # Atributo para armazenar o usuário autenticado

    def __init__(self):
        # Cria o router com o prefixo dinâmico
        self.router = APIRouter(prefix=f"/{self.prefix}", tags=[self.prefix])
    

    async def set_current_user(self, user: User = Depends(get_current_user)):
        # Armazena o usuário autenticado no atributo da classe
        self.current_user = user
    
