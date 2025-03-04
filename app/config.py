from tortoise import Tortoise

DATABASE_URL = "sqlite://db.sqlite3"

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