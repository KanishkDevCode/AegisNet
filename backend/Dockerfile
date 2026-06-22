FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for some ML/Vision packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Temporarily set the entrypoint to the swarm orchestrator
# This will be replaced by the Celery worker command in Phase 2
CMD ["python", "phase4_agent/swarm.py"]
