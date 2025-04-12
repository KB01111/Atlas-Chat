# Multi-stage build for Atlas-Chat frontend
# Stage 1: Install dependencies and build
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Install necessary build dependencies
RUN apk add --no-cache python3 make g++ git

# First copy package files and install node modules
COPY frontend/client/package.json .
RUN npm install

# Then copy the rest of the application
COPY frontend/client/public ./public
COPY frontend/client/src ./src
COPY frontend/client/.eslintrc.json .
COPY frontend/client/tsconfig.json .
COPY frontend/craco.config.js .

# Declare build arguments
ARG REACT_APP_API_BASE_URL=/api
ARG REACT_APP_E2B_CODEINTERPRETER_URL
ARG REACT_APP_SENTRY_DSN
ARG NODE_ENV=production

# Set environment for production build using args
ENV NODE_ENV=$NODE_ENV
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL
ENV REACT_APP_E2B_CODEINTERPRETER_URL=$REACT_APP_E2B_CODEINTERPRETER_URL
ENV REACT_APP_SENTRY_DSN=$REACT_APP_SENTRY_DSN

# Build the application
RUN npm run build

# Stage 2: Nginx for serving the application
FROM nginx:alpine

# Install wget for healthcheck
RUN apk add --no-cache wget

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy health check page for Docker health checks
COPY --from=builder /app/public/health.html /usr/share/nginx/html/health

# Configure nginx with proper routing for SPA and health check
RUN echo 'server { \
    listen 3000; \
    root /usr/share/nginx/html; \
    index index.html; \
    # Handle SPA routing \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    # Health check endpoint required by Windsurf rules \
    location /health { \
        alias /usr/share/nginx/html/health; \
        add_header Content-Type text/html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Add health check as required by Windsurf rules
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1
