# Estágio de build: usa Node.js para construir o projeto
FROM node:22 AS build

WORKDIR /app

# Copia os arquivos de dependências e instala as dependências
COPY package.json yarn.lock ./
RUN yarn install

# Copia o restante do código e faz o build do projeto
COPY . .
RUN yarn build

# Estágio de produção: usa Nginx para servir os arquivos estáticos
FROM nginx:alpine

# Copia os arquivos de build para o diretório do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copia a configuração personalizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe a porta 80
EXPOSE 80

# Inicia o Nginx
CMD ["nginx", "-g", "daemon off;"]