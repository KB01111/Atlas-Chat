# Use bun as the base image
FROM oven/bun:1 as base

# Stage 1: Install dependencies
FROM base AS deps
WORKDIR /app

# Copy package.json and bun.lockb
COPY client/package.json client/bun.lockb* ./

# Install dependencies using bun's frozen lockfile for consistency
RUN bun install --frozen-lockfile

# Stage 2: Build the application
FROM base AS builder
WORKDIR /app

# Copy installed dependencies from the 'deps' stage
COPY --from=deps /app/node_modules ./node_modules

# Copy the rest of the client application code
COPY client/ ./

# Build the React application using the build script defined in package.json
# This should create a 'build' directory
RUN bun run build

# Stage 3: Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

# Copy only necessary production files from the 'builder' stage
# We need package.json and node_modules to run 'serve'
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
# Copy the static build output
COPY --from=builder /app/build ./build

# Expose the port serve will run on (default is 3000)
EXPOSE 3000

# Use 'serve' to host the static files from the 'build' directory
# The '-s' flag ensures that routing works correctly for single-page applications
CMD ["bunx", "serve", "-s", "build"]
