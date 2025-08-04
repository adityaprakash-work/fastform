# Use the official Python image as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY pyproject.toml uv.lock ./
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install pip-tools && \
    pip install --timeout=300 --retries=3 uv && \
    uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system --requirement requirements.txt && \
    apt-get purge -y --auto-remove git

# Copy project
COPY . .

# Expose port (adjust if your app uses a different port)
EXPOSE 8000

# Set the default command to run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
