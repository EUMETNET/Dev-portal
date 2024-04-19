# ---- Build Stage ----
FROM node:21-alpine AS build

WORKDIR /portal-ui/

COPY package*.json .
COPY public/ ./public
COPY index.html .
COPY src/ ./src

# TODO change npm i --> npm ci to respect the package-lock once the vulnerabilites are fixed
RUN npm ci
RUN npm run build

# ---- Runtime stage ----
FROM node:21-alpine AS runtime

WORKDIR /portal-ui/
COPY --from=build /portal-ui/dist ./dist

# Copy the script to generate empty env-config.js file that will be mounted by k8
COPY generate_env-config.sh .

RUN chmod +x generate_env-config.sh
RUN ./generate_env-config.sh > ./dist/env-config.js

# For now install serve to serve the React app
RUN npm install -g serve

EXPOSE 443

CMD ["serve", "-s" ,"dist", "-l", "443"]
