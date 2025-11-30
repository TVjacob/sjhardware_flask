# Use node image for building frontend
FROM node:20-alpine as build

WORKDIR /app
COPY sjhardware-frontend/package*.json ./
RUN npm install
COPY sjhardware-frontend/ ./
RUN npm run build

# Use nginx to serve frontend
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
