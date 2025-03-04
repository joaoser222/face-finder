from fastapi import FastAPI
from app.routes.urls import main_router
from app.config import init_db
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(main_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "API está funcionando!"} 