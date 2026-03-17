# Use official Python image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files first (for layer caching)
COPY pyproject.toml poetry.lock ./

# Install dependencies (no virtualenv needed inside container)
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the rest of the app
COPY . .

# Run the server
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
