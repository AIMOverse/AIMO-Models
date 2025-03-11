# Use the official Python 3.11 slim version as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install `git` to support `git clone`
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set environment variable (NEBULA_API_KEY is used at runtime)
ENV NEBULA_API_KEY=${NEBULA_API_KEY}

# Clone Hugging Face model (avoid exposing HF_ACCESS_TOKEN)
ARG HF_ACCESS_TOKEN
RUN git clone https://Wes1eyyy:${HF_ACCESS_TOKEN}@huggingface.co/Wes1eyyy/AIMO-EmotionModule app/ai/static/models/EmotionModule

# Copy application code into the container
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
