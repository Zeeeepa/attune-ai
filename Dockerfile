# Next.js Production Dockerfile for Railway
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY website/package.json website/package-lock.json* ./
RUN npm ci

# Copy website source
COPY website/ ./

# Build the app (creates .next/standalone)
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build:railway

# Copy static assets to standalone (required for standalone mode)
RUN cp -r .next/static .next/standalone/.next/static
RUN cp -r public .next/standalone/public

# Runtime
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
EXPOSE 3000

# Health check to ensure the application is responding
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

WORKDIR /app/.next/standalone
CMD ["node", "server.js"]
