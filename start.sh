#!/bin/bash
set -e

# Print welcome message
echo "Starting AIMO Emotion Model Service..."

# Ensure model directory exists
MODEL_DIR="/app/app/ai/static/models/EmotionModule"
if [ ! -d "$MODEL_DIR" ] || [ -z "$(ls -A $MODEL_DIR)" ]; then
    echo "Warning: Model directory is empty or does not exist."
    echo "You may need to provide HF_TOKEN as an environment variable to download the model."
    
    # If HF_TOKEN is provided in environment, try to download the model
    if [ -n "$HF_TOKEN" ]; then
        echo "Attempting to download model using provided HF_TOKEN..."
        python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
        tokenizer = AutoTokenizer.from_pretrained('Wes1eyyy/AIMO-EmotionModule', use_auth_token='${HF_TOKEN}'); \
        model = AutoModelForSequenceClassification.from_pretrained('Wes1eyyy/AIMO-EmotionModule', use_auth_token='${HF_TOKEN}'); \
        tokenizer.save_pretrained('/app/app/ai/static/models/EmotionModule'); \
        model.save_pretrained('/app/app/ai/static/models/EmotionModule')"
        
        if [ $? -eq 0 ]; then
            echo "Model downloaded successfully."
        else
            echo "Failed to download model. The service may not function correctly."
        fi
    fi
fi

# Ensure data directory exists
DATA_DIR="/app/app/ai/static/data"
if [ ! -d "$DATA_DIR" ]; then
    echo "Creating data directory..."
    mkdir -p "$DATA_DIR"
fi

# Ensure mapping file exists
MAPPING_FILE="$DATA_DIR/mapping.txt"
if [ ! -f "$MAPPING_FILE" ]; then
    echo "Creating default mapping file..."
    echo -e "happy\nsad\nangry\nfearful\nsurprised\ndisgust" > "$MAPPING_FILE"
fi

# Ensure Nginx log directory exists
mkdir -p /var/log/nginx
# Ensure Nginx cache directories exist
mkdir -p /var/cache/nginx/client_temp \
         /var/cache/nginx/proxy_temp \
         /var/cache/nginx/fastcgi_temp \
         /var/cache/nginx/uwsgi_temp \
         /var/cache/nginx/scgi_temp

# Set correct permissions
chown -R www-data:www-data /var/log/nginx /var/cache/nginx

# Check supervisord configuration
echo "Checking supervisord configuration..."
supervisord -c /etc/supervisor/conf.d/supervisord.conf -t

# Set forced CPU mode (if specified)
if [ "${FORCE_CPU}" = "1" ]; then
    echo "Forcing CPU mode as specified by FORCE_CPU=1"
    export CUDA_VISIBLE_DEVICES=""
fi

# Display system information
echo "System information:"
echo "Python version: $(python --version)"
echo "CPU cores: $(grep -c processor /proc/cpuinfo)"
echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
echo "Device mode: $(if [ "${FORCE_CPU}" = "1" ]; then echo "CPU (forced)"; elif command -v nvidia-smi > /dev/null; then echo "GPU"; else echo "CPU"; fi)"

# Test network connectivity (optional)
echo "Testing network connectivity..."
if curl -s --head  --request GET https://huggingface.co | grep "200 OK" > /dev/null; then
    echo "Hugging Face API is reachable."
else
    echo "Warning: Cannot reach Hugging Face API. If the model needs to be downloaded, it may fail."
fi

# Start the application
echo "Starting supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf