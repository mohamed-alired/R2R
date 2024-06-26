FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ musl-dev curl libffi-dev gfortran libopenblas-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the pyproject.toml and poetry.lock files for installing dependencies
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and configure it to create a virtual environment
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create true \
    && poetry install -E local-embedding --no-dev --no-interaction --no-ansi \
    && rm -rf ~/.cache/pip

# Copy the rest of the application code
COPY . /app

# Install gunicorn and uvicorn
RUN poetry run pip install --no-cache-dir gunicorn uvicorn

# Expose the port
EXPOSE 8000

# Set the command to run the application with Gunicorn
CMD ["poetry", "run", "gunicorn", "r2r.examples.servers.configurable_pipeline:r2r_app", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "8", "--timeout", "0", "--worker-class", "uvicorn.workers.UvicornWorker"]
