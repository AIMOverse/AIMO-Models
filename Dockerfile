FROM python:3.9-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    curl \
    nginx \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install specific version of supervisor
RUN pip install supervisor==4.2.5

# Create necessary directories
RUN mkdir -p /var/log/supervisor /app/app/ai/static/models/EmotionModule /app/app/ai/static/data

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

# Copy application code
COPY app ./app

# Copy Nginx configuration files
COPY nginx.conf /etc/nginx/nginx.conf
COPY aimo.conf /etc/nginx/conf.d/default.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY aimo_models.conf /etc/supervisor/conf.d/aimo_models.conf

# Add startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Hugging Face token will be provided at build time
ARG HF_TOKEN=""
ENV HF_TOKEN=${HF_TOKEN}

# Download models at build time (if token is provided)
RUN if [ -n "$HF_TOKEN" ]; then \
        python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
        tokenizer = AutoTokenizer.from_pretrained('Wes1eyyy/AIMO-EmotionModule', use_auth_token='${HF_TOKEN}'); \
        model = AutoModelForSequenceClassification.from_pretrained('Wes1eyyy/AIMO-EmotionModule', use_auth_token='${HF_TOKEN}'); \
        tokenizer.save_pretrained('/app/app/ai/static/models/EmotionModule'); \
        model.save_pretrained('/app/app/ai/static/models/EmotionModule')"; \
    fi

# API_KEY
ENV NEBULA_API_KEY = ""

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Expose Nginx port
EXPOSE 80 5000

# Startup command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]