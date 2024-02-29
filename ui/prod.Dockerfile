# ---- Build Stage ----
FROM node:21-alpine AS build

WORKDIR /portal-ui/

COPY package*.json .
COPY public/ ./public
COPY src/ ./src

# Define args needed by React app
ARG REACT_APP_ENV=PRODUCTION
ARG REACT_APP_KEYCLOAK_URL
ARG REACT_APP_KEYCLOAK_REALM
ARG REACT_APP_KEYCLOAK_CLIENTID
ARG REACT_APP_LOGOUT_URL
ARG REACT_APP_BACKEND_URL

# TODO change npm i --> npm ci to respect the package-lock once the vulnerabilites are fixed
RUN npm i
RUN npm run build

# ---- Runtime stage ----
FROM node:21-alpine AS runtime

WORKDIR /portal-ui/
COPY --from=build /portal-ui/build ./build

# For now install serve to serve the React app
RUN npm install -g serve

EXPOSE 443

CMD ["serve", "-s" ,"build", "-l", "443"]
