# Production

#FROM node:18 AS builder
FROM node:18
WORKDIR /app

COPY . .

RUN npm install
#RUN npm run build

#FROM nginx:alpine

#COPY --from=builder /app/dist /usr/share/nginx/html

#EXPOSE 80
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]