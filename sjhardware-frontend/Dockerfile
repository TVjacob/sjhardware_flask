# ----------- BUILD STAGE -----------
    FROM node:18-alpine AS build

    WORKDIR /app
    
    # Copy dependency files
    COPY package*.json ./
    
    # Install dependencies
    RUN npm install
    
    # Copy source
    COPY . .
    
    # Build for production
    RUN npm run build
    
    
    # ----------- PRODUCTION STAGE -----------
    FROM node:18-alpine
    
    WORKDIR /app
    
    # Install a simple static server
    RUN npm install -g serve
    
    # Copy only the production build
    COPY --from=build /app/dist ./dist
    
    EXPOSE 5173
    
    # Start the optimized, built app
    CMD ["serve", "-s", "dist", "-l", "5173"]
    