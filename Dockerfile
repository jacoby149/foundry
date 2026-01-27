FROM oven/bun:latest AS frontend-build

WORKDIR /app
COPY ui ./ui
WORKDIR /app/ui
RUN bun install
RUN bun run build

# --- FIX: Use linux/amd64 for M3 Mac compatibility ---
FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

# --- FIX: Updated package names for Debian Bookworm/Trixie ---
# 'libgl1-mesa-glx' is deprecated. We use 'libgl1' instead.
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfiles
COPY api/Pipfile api/Pipfile.lock ./

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy backend code
COPY api/ /app/

# Copy frontend static build output
COPY --from=frontend-build /app/ui/dist /static/ui

EXPOSE 8000

# Run
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
