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
import sys,traceback
import json

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

def chunk_array(arr, chunk_size):
    for i in range(0, len(arr), chunk_size):
        yield arr[i:i + chunk_size]

def logger_info(name, message):
    _logger = logging.getLogger(name)
    getattr(_logger, "info")(message)

def logger_error(name, exception_obj):
    _logger = logging.getLogger(name)
    tb = traceback.extract_tb(exception_obj.__traceback__)
    for frame in tb:
        context = json.dumps({
            "line": frame.lineno,
            "function": frame.name,
            "code": frame.line
        })
        _logger.error(f"{str(exception_obj)} - {context}")

def setup_logging():
    try:
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
    except Exception as e:
        logger_error("setup_logging", e)

class QueryBuilder:
    def __init__(self):
        self.query = ""
    
    def apply(self, clause, *args,separator=", "):
        self.query += f"{clause} {separator.join(args)} "
        return self

    def build(self):
        return self.query.strip()

async def execute_raw_sql(raw_sql: str,has_result: bool = True):
    """
    Executa uma query SQL bruta usando Tortoise-ORM.
    Args:
        raw_sql (str): A query SQL a ser executada.
        has_result (bool, optional): Indica se a query deve retornar resultados. Padrão é True.

    Returns:
        Any: O resultado da query.
    """
    try:
        from tortoise import transactions,connections

        result = None
        # Obter conexão do banco de dados
        conn = connections.get("default")
        # Executar a query SQL
        if(has_result):
            result = await conn.execute_query_dict(raw_sql)
            return result
        else:
            async with transactions.in_transaction():
                await conn.execute_query(raw_sql)
        return result
    except Exception as e:
        logger_error(__name__,e)
        raise 
