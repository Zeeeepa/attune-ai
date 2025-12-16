# Next.js Production Dockerfile for Railway
# Build context: website/
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source
COPY . .

# Build the app
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build:railway

# Copy static assets to standalone
RUN cp -r .next/static .next/standalone/.next/static
RUN cp -r public .next/standalone/public

# Runtime
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
EXPOSE 3000

WORKDIR /app/.next/standalone
CMD ["node", "server.js"]
