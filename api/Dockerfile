# Usa uma imagem base com Python
FROM python:3.11

# Instala o Netcat e outras dependências úteis
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Define o comando padrão ao iniciar o container
CMD ["sh", "start.sh"]