from tortoise import Tortoise
import os

# Verifica se a URL do banco de dados foi definida
if not os.getenv("DATABASE_POSTGRES_URL"):
    raise ValueError("A variável de ambiente DATABASE_POSTGRES_URL não está definida.")

# Configuração do Tortoise ORM
TORTOISE_ORM = {
    "connections": {
        "default": os.getenv("DATABASE_POSTGRES_URL"),  # Usa a URL do banco de dados da variável de ambiente
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user", 
                "app.models.collection", 
                "app.models.photo",
                "app.models.archive",
                "app.models.face", 
                "app.models.search", 
                "app.models.search_face",
                "app.models.session",
                "app.models.job"
            ],
            "default_connection": "default",
        }
    }
}

async def init_db():
    """
    Inicializa o banco de dados usando o Tortoise ORM.
    """
    await Tortoise.init(config=TORTOISE_ORM)

    # Gera os esquemas do banco de dados (cria as tabelas, se não existirem)
    await Tortoise.generate_schemas()

async def close_db():
    """
    Fecha as conexões com o banco de dados.
    """
    await Tortoise.close_connections()