from fastapi import FastAPI
from app.config import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.user_controller import UserController
from app.controllers.collection_controller import CollectionController
from app.controllers.photo_controller import PhotoController
from app.controllers.search_controller import SearchController

app = FastAPI(title="FastAPI com Tortoise ORM")

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluindo as rotas
app.include_router(UserController().router, prefix="/api")
app.include_router(CollectionController().router, prefix="/api")
app.include_router(PhotoController().router, prefix="/api")
app.include_router(SearchController().router, prefix="/api")

@app.lifespan("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "API está funcionando!"} 