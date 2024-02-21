FROM node:21-alpine

WORKDIR /portal-ui/

COPY public/ /portal-ui/public
COPY src/ /portal-ui/src
COPY package.json /portal-ui/

COPY dev.env /portal-ui/
COPY .env /portal-ui/

RUN npm install
RUN npm run build
RUN npm install -g serve

EXPOSE 443

CMD ["serve", "-s" ,"build", "-l", "443"]
