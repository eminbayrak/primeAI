FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY server.py .

# Create directories
RUN mkdir -p temp models

# Set environment variables
ENV PORT=5000
ENV USE_GPU=0

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "server.py"]
