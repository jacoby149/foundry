FROM oven/bun:latest AS frontend-build

WORKDIR /app
COPY ui ./ui
WORKDIR /app/ui
RUN bun install
RUN bun run build

FROM python:3.13-slim

WORKDIR /app

# Install pipenv in Python image
RUN pip install --no-cache-dir pipenv

# Copy only Pipfile and Pipfile.lock first, for better Docker cache
COPY api/Pipfile api/Pipfile.lock ./

# Install all dependencies (creates virtualenv in /root/.local/share/virtualenvs/)
RUN pipenv install --deploy --ignore-pipfile

# Now copy the rest of your FastAPI app code
COPY api/ /app/

# # Copy frontend static build output
COPY --from=frontend-build /app/ui/dist /static/ui

EXPOSE 8000

# Run under pipenv virtual env context
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
