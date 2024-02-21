FROM node:21-alpine as build

WORKDIR /portal-ui/

COPY public/ /portal-ui/public
COPY src/ /portal-ui/src
COPY package.json /portal-ui/

COPY dev.env /portal-ui/
COPY .env /portal-ui/

RUN npm install
RUN npm run build


FROM build as deploy

WORKDIR /portal-ui/

RUN npm install -g serve

EXPOSE 3002

CMD ["serve", "-s" ,"build", "-l", "3002"]
