#!/bin/bash

# Entrypoint script for RunPod Serverless models
# This script starts ComfyUI in the background and then starts the handler

set -e  # Exit on error

echo "========================================"
echo "Starting StoryStudio RunPod Serverless"
echo "========================================"

# Start ComfyUI in the background
echo "Starting ComfyUI server..."
python /ComfyUI/main.py --listen --port 8188 > /var/log/comfyui.log 2>&1 &
COMFY_PID=$!

echo "ComfyUI started with PID: $COMFY_PID"

# Wait for ComfyUI to be ready
echo "Waiting for ComfyUI to be ready..."
MAX_WAIT=120  # 2 minutes
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s http://127.0.0.1:8188/ > /dev/null 2>&1; then
        echo "✅ ComfyUI is ready!"
        break
    fi
    
    if [ $((WAIT_COUNT % 10)) -eq 0 ]; then
        echo "Still waiting for ComfyUI... ($WAIT_COUNT/$MAX_WAIT)"
    fi
    
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo "❌ Error: ComfyUI failed to start within $MAX_WAIT seconds"
    echo "ComfyUI logs:"
    cat /var/log/comfyui.log
    exit 1
fi

# Display environment info
echo ""
echo "Environment Configuration:"
echo "- CUDA Available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "- GPU Count: $(python -c 'import torch; print(torch.cuda.device_count())')"
echo "- Python Version: $(python --version)"
echo "- ComfyUI URL: http://127.0.0.1:8188"

# Check if R2 storage is configured
if [ -n "$R2_BUCKET_NAME" ]; then
    echo "- R2 Storage: Enabled (bucket: $R2_BUCKET_NAME)"
else
    echo "- R2 Storage: Disabled (no R2_BUCKET_NAME set)"
fi

echo ""
echo "========================================"
echo "Starting RunPod Handler..."
echo "========================================"

# Start the handler (this becomes the main process)
exec python /handler.py
