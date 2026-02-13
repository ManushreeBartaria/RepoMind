FROM node:22 AS builder

WORKDIR /mind/frontend 

COPY package*.json ./

RUN npm install 

From node:22
WORKDIR /mind/frontend
COPY --from=builder usr/local usr/local
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
