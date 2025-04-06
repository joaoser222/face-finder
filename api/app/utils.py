from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.models.user import User
from app.models.session import Session
from datetime import datetime, timezone
from passlib.context import CryptContext
import uuid
import os
import logging
from logging.handlers import RotatingFileHandler


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

# Função para gerar um nome de arquivo único
def generate_unique_filename(original_filename: str) -> str:
    _, ext = os.path.splitext(original_filename)
    unique_id = uuid.uuid4().hex
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{unique_id}{ext.lower()}"

def setup_logging():
    # Formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # Configuração do logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Cria o diretório de logs se não existir
    os.makedirs("/app/logs", exist_ok=True)

    # Handler para arquivo (com rotação)
    file_handler = RotatingFileHandler(
        filename="/app/logs/app.log",
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para console (opcional)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Desabilitar logs duplicados do uvicorn
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn").propagate = False