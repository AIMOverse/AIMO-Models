FROM python:3.9-slim

# Install necessary system dependencies, including Nginx
RUN apt-get update && apt-get install -y \
    libssl-dev \
    curl \
    nginx \
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
RUN pip install supervisor==4.2.5 gunicorn==23.0.0

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

# Set API_KEY
ENV NEBULA_API_KEY = ""

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Expose Nginx port
EXPOSE 80 5000

# Startup command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]