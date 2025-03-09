from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.models.user import User
from app.models.session import Session
from datetime import datetime, timezone
from passlib.context import CryptContext

security = HTTPBearer()

# Configuração do Passlib para criptografia de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_user(token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verifica se o token foi fornecido
    if not token.credentials:
        raise credentials_exception

    # Busca a sessão no banco de dados pelo token
    session = await Session.get_or_none(token=token.credentials)
    if not session:
        raise credentials_exception

    # Verifica se o token expirou
    if session.expires_at < datetime.now(timezone.utc):
        raise credentials_exception

    # Busca o usuário associado à sessão
    user = await User.get_or_none(id=session.user_id)
    if not user:
        raise credentials_exception

    return user

# Função para criptografar uma senha
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Função para verificar uma senha
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
