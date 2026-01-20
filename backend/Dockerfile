# Use a slim Python base image to keep the container lightweight
# Slim images reduce attack surface and build time
FROM python:3.9-slim

# Set a working directory inside the container
# All subsequent commands run from here
WORKDIR /app

# Install system-level dependencies required by Python packages
# - gcc: needed for some Python wheels
# - libgl1: required by PIL / image processing
RUN apt-get update && apt-get install -y \
    gcc \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list first
# This allows Docker to cache pip installs unless requirements change
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app ./app

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the FastAPI server
# --host 0.0.0.0 is required so Docker can expose it
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]