from click import INT
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta,timezone
from uuid import uuid4
from app.models.user import User
from app.models.session import Session
from app.utils import get_current_user, get_password_hash, verify_password
import os

SESSION_EXPIRE_MINUTES = os.getenv("SESSION_EXPIRE_MINUTES")

class AuthController:
    def __init__(self):
        # Cria o router com o prefixo dinâmico
        self.router = APIRouter(prefix=f"/auth", tags=["auth"])

        # Define as rotas
        self.router.add_api_route("/register", self.register, methods=["POST"])
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/logout", self.logout, methods=["POST"])
    
    async def create_session(self,user: User):
        try:
            token = str(uuid4())
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=int(SESSION_EXPIRE_MINUTES))
            await Session.create(user=user, token=token, expires_at=expires_at)
            return {"token": token, "expires_at": expires_at}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Rota para registrar um novo usuário
    async def register(self,request: Request):
        try:
            data = await request.json()
            user = await User.create(**data,password_hash=get_password_hash(data["password"]))
            session = await self.create_session(user)
            return session
        except Exception as e:
            raise

    # Rota para fazer login e gerar um token de sessão
    async def login(self,request: Request):
        try:
            data = await request.json()
            user = await User.get_or_none(email=data["email"])
            if not user or not verify_password(data["password"], user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuário ou senha incorretos",
                    )
            session = await self.create_session(user)
            return session
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Rota para fazer logout
    async def logout(self,current_user: User = Depends(get_current_user)):
        try:
            session = await Session.get_or_none(user=current_user)
            if session:
                await session.delete()
            return {"message": "Logout realizado com sucesso"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
