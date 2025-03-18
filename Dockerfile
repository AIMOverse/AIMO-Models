# Use the official NVIDIA CUDA 12.4 runtime image (Ubuntu 22.04)
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Set the working directory
WORKDIR /app

# Update system packages and install necessary dependencies (including git and Python)
RUN apt-get update && apt-get install -y \
    git \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN python3.11 -m pip install --upgrade pip

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set environment variables
ENV NEBULA_API_KEY=${NEBULA_API_KEY}
ENV SECRET_KEY=${SECRET_KEY}
ENV ADMIN_API_KEY=${ADMIN_API_KEY}
ENV DATABASE_URL=${DATABASE_URL}

# Clone the Hugging Face model repository using a secure token
ARG HF_ACCESS_TOKEN
RUN git clone https://Wes1eyyy:${HF_ACCESS_TOKEN}@huggingface.co/Wes1eyyy/AIMO-EmotionModule app/ai/static/models/EmotionModule

# Copy the application code into the container
COPY . .

# Expose port 8000 for the application
EXPOSE 8000

# Run the application using Gunicorn with Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
