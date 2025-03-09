#!/bin/sh

# Aplica as migrações (se houver novas)
aerich upgrade

# Inicia o Uvicorn
echo "Iniciando o Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000