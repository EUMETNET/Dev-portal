# ---- Build Stage ----
FROM node:21-alpine AS build

WORKDIR /portal-ui/

COPY package*.json .
COPY public/ ./public
COPY index.html .
COPY src/ ./src

RUN npm ci
RUN npm run build

# ---- Runtime stage ----
FROM node:21-alpine AS runtime

WORKDIR /portal-ui/
COPY --from=build /portal-ui/dist ./dist

# For now install serve to serve the React app
RUN npm install -g serve

EXPOSE 443

CMD ["serve", "-s" ,"dist", "-l", "443"]
