# Use Node.js 20 as base image
FROM node:20-slim

WORKDIR /app

# Copy package files from website directory
COPY website/package.json website/package-lock.json* ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy website files
COPY website/ ./

# Build the Next.js application (using Railway-specific build)
RUN npm run build:railway

# Expose port
EXPOSE 8080

ENV PORT=8080
ENV NODE_ENV=production

# Start the application
CMD ["npm", "run", "start"]
