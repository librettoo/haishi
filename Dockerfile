# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set Hugging Face cache directory to a writable location
ENV HF_HOME=/app/cache

WORKDIR /app

# Create a cache directory for Hugging Face models
RUN mkdir -p /app/cache && chmod 777 /app/cache

# Create a non-privileged user to run the app
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user
USER appuser

# Copy the source code
COPY . .

# Expose the port
EXPOSE 8000

# Run the application
CMD gunicorn 'app:app' --bind=0.0.0.0:8000
