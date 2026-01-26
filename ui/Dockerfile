# Use the official Bun image for 2026
FROM oven/bun:latest

WORKDIR /app

# Copy package files first for better caching
COPY package.json bun.lock ./
RUN bun install 

# Copy the rest of the code
COPY . .

EXPOSE 5173

# Start the dev server
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]
