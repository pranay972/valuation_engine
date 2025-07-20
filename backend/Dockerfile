# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy Poetry files first for better caching
COPY pyproject.toml ./
# If you have poetry.lock, uncomment the next line
# COPY poetry.lock ./

# Install dependencies (no venv)
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the backend code
COPY backend/ ./backend/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 