# Usa uma imagem base com Python
FROM python:3.11

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Cria o diretório para armazenar as imagens
RUN mkdir -p /app/static/search
RUN mkdir -p /app/static/photos

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Define a variável de ambiente para o Celery conectar ao Redis
ENV CELERY_BROKER_URL=redis://redis:6379/0

# Define o comando padrão ao iniciar o container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
