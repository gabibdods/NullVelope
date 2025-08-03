FROM node:18

WORKDIR /app

COPY . .

RUN npm install -g Haraka

RUN npm install --production

EXPOSE 25

ENTRYPOINT ["haraka", "-c", "."]