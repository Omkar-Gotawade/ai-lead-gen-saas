FROM node:18-slim AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy app files and build
COPY . .
RUN npm run build

# Production stage
FROM node:18-slim

WORKDIR /app

# Install serve to host the built files
RUN npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 5173

# Serve the built app
CMD ["serve", "-s", "dist", "-l", "5173", "--no-clipboard"]
