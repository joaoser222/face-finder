#!/bin/sh

# Espera o banco de dados ficar pronto
while ! nc -z postgres 5432; do
  echo "Esperando o banco de dados..."
  sleep 1
done

# Aplica as migrações (se houver novas)
aerich upgrade

# Inicia o Uvicorn
echo "Iniciando o Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000