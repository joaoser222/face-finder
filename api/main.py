from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import init_db,close_db
from app.controllers.auth_controller import AuthController
from app.controllers.collection_controller import CollectionController
from app.controllers.photo_controller import PhotoController
from app.controllers.search_controller import SearchController

# Usando o lifespan para gerenciar eventos de startup e shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # Inicializa o banco de dados
    yield
    await close_db()  # Fecha as conexões com o banco de dados


# Cria a aplicação FastAPI com o lifespan
app = FastAPI(
    title="FaceFinder API",
    lifespan=lifespan
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (ajuste para produção)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

# Incluindo as rotas
app.include_router(AuthController().router)
app.include_router(CollectionController().router)
app.include_router(PhotoController().router)
app.include_router(SearchController().router)

# Rota de teste
@app.get("/")
async def root():
    return {"message": "API está funcionando!"}