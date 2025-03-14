# Stage 1: Build the React application with Vite
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY ./frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy all frontend files
COPY ./frontend/ ./

# Build the app
RUN npm run build

# Stage 2: Setup production environment
FROM node:18-alpine

WORKDIR /app

# Install serve for a production server
RUN npm install -g serve

# Copy build files from the previous stage
COPY --from=build /app/dist ./dist

# Set environment variables
ENV NODE_ENV=production

# Expose the port
EXPOSE 4173

# Set the command to serve the app
CMD serve -s dist -l 4173
