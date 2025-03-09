from tortoise import Tortoise
import os

# Obtém a URL do banco de dados das variáveis de ambiente
DATABASE_POSTGRES_URL = os.getenv("DATABASE_POSTGRES_URL")

# Verifica se a URL do banco de dados foi definida
if not DATABASE_POSTGRES_URL:
    raise ValueError("A variável de ambiente não está definida.")

async def init_db():
    """
    Inicializa o banco de dados usando o Tortoise ORM.
    """
    await Tortoise.init(
        db_url=DATABASE_POSTGRES_URL,
        modules={
            'models': [
                'app.models.user', 
                'app.models.collection', 
                'app.models.photo', 
                'app.models.face', 
                'app.models.search', 
                'app.models.search_collection',
                'app.models.session'
            ]
        }
    )
    # Gera os esquemas do banco de dados (cria as tabelas, se não existirem)
    await Tortoise.generate_schemas()

async def close_db():
    """
    Fecha as conexões com o banco de dados.
    """
    await Tortoise.close_connections()