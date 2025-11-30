# Use Node.js image for frontend dev
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json & package-lock.json
COPY sjhardware-frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY sjhardware-frontend/ ./


# Expose port for dev server
EXPOSE 5173

# Run frontend in development mode
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
