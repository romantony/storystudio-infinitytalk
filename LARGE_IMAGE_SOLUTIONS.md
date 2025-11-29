# Alternative Deployment Strategies for Large Docker Images

## Problem
The InfiniteTalk Docker image is 102GB with individual layers up to 17GB, causing network timeouts when pushing to Docker Hub from typical home internet connections.

## Solution 1: Network Volume Approach (RECOMMENDED)

### Benefits
- ✅ Smaller image (~30GB without models)
- ✅ Faster deployments
- ✅ Models shared across all pods
- ✅ One-time model download
- ✅ Better for scaling

### Implementation

#### Step 1: Create a network volume image

Build a smaller base image that downloads models on first run:

```dockerfile
# Modify Dockerfile to remove model downloads
# Models will be downloaded to network volume instead
```

#### Step 2: Create Network Volume on RunPod
- Size: 50GB
- Mount path: `/workspace/models`

#### Step 3: First Run Downloads Models
The entrypoint script checks if models exist, downloads if needed:
```bash
if [ ! -f "/workspace/models/wan2.1-i2v-14b-480p-Q8_0.gguf" ]; then
    echo "Downloading models to network volume..."
    wget models... -P /workspace/models/
fi
```

#### Step 4: Symlink to ComfyUI
```bash
ln -sf /workspace/models/* /ComfyUI/models/
```

### Cost Comparison
- **Current:** 102GB image push time: 2-4 hours per update
- **Network Volume:** 30GB image push: 30-60 minutes, models download once

## Solution 2: Push from Cloud Instance

### Using RunPod Instance to Build and Push

```bash
# On RunPod GPU instance (has fast upload)
1. SSH into RunPod instance
2. Install Docker
3. Clone your repo
4. Build image
5. Push to Docker Hub (fast upload)
```

### Cost
- RunPod instance: ~$0.40/hr × 2hrs = $0.80 one-time

## Solution 3: Use Docker Layer Caching

### Split into Base + Model Layers

```dockerfile
# Base image (push once, rarely changes)
FROM storystudio/base:latest

# Model downloads (separate layers)
RUN wget model1...
RUN wget model2...
RUN wget model3...
```

Each model is a separate layer. When pushing:
- Only changed layers upload
- Base layer pushes once
- Subsequent pushes only upload new model layers

## Solution 4: Alternative Registries

### GitHub Container Registry (ghcr.io)
- Free for public images
- Better for large images
- Integrated with GitHub Actions

```bash
docker tag storystudio/infinitetalk:latest ghcr.io/romantony/storystudio-infinitetalk:latest
echo $GITHUB_TOKEN | docker login ghcr.io -u romantony --password-stdin
docker push ghcr.io/romantony/storystudio-infinitetalk:latest
```

### AWS ECR
- Better upload speeds from AWS regions
- Pay per GB stored
- No transfer fees within AWS

## Recommended Approach for Your Use Case

**Option A: Network Volume (Best for Production)**

1. Modify Dockerfile to remove model downloads
2. Create download script for models
3. Push smaller base image (~30GB)
4. First pod downloads models to network volume
5. All future pods use cached models

**Implementation Time:** 2-3 hours
**Cost:** Network volume $4/month for 50GB
**Benefits:** Fastest deployments, best for scaling

**Option B: Push from RunPod Instance (Quick Fix)**

1. Deploy a RunPod GPU instance (RTX 3090)
2. Install Docker on the instance
3. Transfer your built image or build on instance
4. Push from RunPod (fast upload to Docker Hub)
5. Terminate instance

**Implementation Time:** 30-60 minutes
**Cost:** ~$0.80 one-time
**Benefits:** Quick solution, image ready immediately

## Network Volume Setup Script

```bash
#!/bin/bash
# download_models.sh - Run on first startup

MODEL_DIR="/workspace/models"
COMFYUI_MODEL_DIR="/ComfyUI/models"

mkdir -p $MODEL_DIR

# Check and download models
if [ ! -f "$MODEL_DIR/wan2.1-i2v-14b-480p-Q8_0.gguf" ]; then
    echo "Downloading InfiniteTalk models..."
    
    wget https://huggingface.co/.../Wan2_1-InfiniteTalk_Single.gguf \
        -O $MODEL_DIR/Wan2_1-InfiniteTalk_Single.gguf
    
    wget https://huggingface.co/.../wan2.1-i2v-14b-480p-Q8_0.gguf \
        -O $MODEL_DIR/wan2.1-i2v-14b-480p-Q8_0.gguf
    
    # ... other models
    
    echo "✅ Models downloaded"
else
    echo "✅ Models already exist in network volume"
fi

# Create symlinks
ln -sf $MODEL_DIR/*.gguf $COMFYUI_MODEL_DIR/diffusion_models/
ln -sf $MODEL_DIR/*.safetensors $COMFYUI_MODEL_DIR/text_encoders/

echo "✅ Models linked to ComfyUI"
```

## Modified Entrypoint

```bash
#!/bin/bash
# entrypoint.sh with network volume support

# Download models if using network volume
if [ -d "/workspace" ]; then
    echo "Network volume detected, checking models..."
    /download_models.sh
fi

# Start ComfyUI
python /ComfyUI/main.py --listen --port 8188 &

# ... rest of entrypoint
```

## Immediate Action

For right now, I recommend:

1. **Stop current push** (it will keep failing)
2. **Choose one approach:**
   - **Quick:** Use RunPod instance to push (1 hour setup)
   - **Best:** Implement network volume approach (2-3 hours setup)
3. **Update deployment docs** with chosen approach

Would you like me to:
- A) Create the network volume version of the Dockerfile?
- B) Create instructions for pushing from RunPod instance?
- C) Try alternative registry (GitHub Container Registry)?
