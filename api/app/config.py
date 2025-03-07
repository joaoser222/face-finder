from tortoise import Tortoise
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': [
            'app.models.user', 
            'app.models.collection', 
            'app.models.photo', 
            'app.models.face', 
            'app.models.search', 
            'app.models.search_collection'
        ]}
    )
    await Tortoise.generate_schemas() 