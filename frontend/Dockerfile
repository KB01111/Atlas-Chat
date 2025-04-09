# Use bun as the base image
FROM oven/bun:1 as base

# Stage 1: Install dependencies
FROM base AS deps
WORKDIR /workspace

COPY package.json bun.lockb* ./
COPY frontend/ ./frontend/
COPY frontend/packages/ ./frontend/packages/
COPY frontend/packages/data-provider/ ./frontend/packages/data-provider/

# Explicitly copy Craco config
# Copy the real craco.config.js into frontend directory inside container
COPY frontend/craco.config.js ./frontend/craco.config.js
COPY frontend/client/ ./frontend/client/

RUN bun install --frozen-lockfile

# Build the librechat-data-provider package to generate dist/
RUN bun run --cwd frontend/packages/data-provider build

# Debug: list the dist directory contents after build
RUN ls -R frontend/packages/data-provider/dist
RUN ls -l frontend/packages/data-provider/dist/react-query

# Stage 2: Build the application
FROM base AS builder
WORKDIR /app

# Copy installed dependencies from the 'deps' stage
COPY --from=deps /workspace/node_modules ./node_modules

# Copy the rest of the client application code
COPY --from=deps /workspace/frontend/client ./frontend/client

# Set environment variables for production build
ARG REACT_APP_API_BASE_URL
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}

# Build the React application using the build script defined in package.json
# Debug: print Craco config to verify alias is included
RUN echo "CRACO CONFIG:" && cat frontend/client/craco.config.js

WORKDIR /app/frontend/client
RUN bun run build

# Stage 3: Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

# Copy only necessary production files from the 'builder' stage
COPY --from=builder /app/frontend/client/build ./build

# Install serve globally for production hosting
RUN bun install -g serve

# Expose the port serve will run on (default is 3000)
EXPOSE 3000

# Use 'serve' to host the static files from the 'build' directory
# The '-s' flag ensures that routing works correctly for single-page applications
CMD ["serve", "-s", "build", "-l", "tcp://0.0.0.0:3000"]
