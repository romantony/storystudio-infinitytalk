# RunPod Deployment Guide

## Docker Image Information

**Image Name:** `storystudio/infinitetalk:latest`
**Base:** PyTorch 2.9.1, CUDA 12.6.3, Python 3.12.3
**Size:** ~40GB (includes all models)

## Hardware Requirements

### Minimum Requirements (OOM on 6GB):
- GPU: NVIDIA with 6GB VRAM (RTX 3050, etc.)
- RAM: 8GB system RAM
- Storage: 50GB disk space

### Recommended Requirements:
- GPU: NVIDIA with 16GB+ VRAM (RTX 4090, A6000, etc.)
- RAM: 16GB+ system RAM
- Storage: 50GB disk space

**Note:** The InfiniteTalk models require significant VRAM. 6GB will cause Out of Memory errors. For production use, deploy on RunPod GPUs with 16GB+ VRAM.

## Pushing to Docker Hub

```bash
# Tag the image (if needed)
docker tag storystudio/infinitetalk:latest yourusername/infinitetalk:latest

# Login to Docker Hub
docker login

# Push the image
docker push yourusername/infinitetalk:latest
```

## RunPod Template Configuration

### 1. Container Configuration
- **Container Image:** `yourusername/infinitetalk:latest`
- **Container Disk:** 50GB minimum
- **Expose HTTP Port:** 8188
- **Docker Command:** Leave empty (uses ENTRYPOINT)

### 2. Environment Variables

Required for R2 Storage:
```
R2_ACCOUNT_ID=620baa808df08b1a30d448989365f7dd
R2_BUCKET_NAME=storystudio
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_PUBLIC_URL=https://parentearn.com
```

Optional:
```
COMFYUI_DISABLE_AUTO_UPDATE=true
COMFYUI_DISABLE_METADATA=true
```

### 3. GPU Configuration
- **Recommended:** RTX A6000 (48GB VRAM) or RTX 4090 (24GB VRAM)
- **Minimum:** RTX 3090 (24GB VRAM)
- **Not Recommended:** RTX 3050 (6GB VRAM) - will cause OOM

### 4. Volume Configuration (Optional)
If using network volumes for model caching:
- Mount point: `/ComfyUI/models`
- Size: 30GB minimum

## API Usage

### Request Format

```json
{
  "input": {
    "input_type": "image",
    "person_count": "single",
    "prompt": "A person giving a speech",
    "image_url": "https://example.com/image.jpg",
    "wav_url": "https://example.com/audio.mp3",
    "width": 512,
    "height": 512,
    "max_frame": 150,
    "use_r2_storage": true
  }
}
```

### Parameters

- **input_type**: `"image"` or `"video"`
- **person_count**: `"single"` or `"multi"`
- **prompt**: Text description of the video
- **image_url**: URL to input image (required if input_type=image)
- **video_url**: URL to input video (required if input_type=video)
- **wav_url**: URL to audio file (MP3 or WAV)
- **width**: Video width (default: 512)
- **height**: Video height (default: 512)
- **max_frame**: Maximum frames to generate (default: 150, ~5 seconds at 30fps)
  - **Reduce to 30-60 for 6GB VRAM**
  - Use 150+ for 16GB+ VRAM
- **use_r2_storage**: Upload output to R2 (true/false)

### Response Format

Success:
```json
{
  "output_files": [
    {
      "path": "/ComfyUI/output/video.mp4",
      "url": "https://parentearn.com/output/video.mp4"
    }
  ],
  "execution_time": 120.5
}
```

Error:
```json
{
  "error": "Out of memory error message"
}
```

## Testing Locally

```bash
# Start the container
docker-compose up -d infinitetalk

# Copy test input
docker cp test_input.json storystudio-infinitytalk-infinitetalk-1:/test_input.json

# Restart to trigger processing
docker-compose restart infinitetalk

# Check logs
docker logs -f storystudio-infinitytalk-infinitetalk-1
```

## Troubleshooting

### Out of Memory Errors
**Symptom:** `torch.OutOfMemoryError: Allocation on device`

**Solutions:**
1. Deploy on GPU with more VRAM (16GB+)
2. Reduce `max_frame` parameter (try 30-60 instead of 150)
3. Ensure no other processes are using GPU memory

### Workflow Fails to Queue
**Symptom:** `Connection refused` or `ComfyUI not ready`

**Solutions:**
1. Check ComfyUI logs: `docker logs container_name`
2. Verify GPU is detected: Check "CUDA Available: True" in logs
3. Wait longer for startup (can take 2-3 minutes on first run)

### Models Not Loading
**Symptom:** `Model file not found`

**Solutions:**
1. Verify all models were downloaded during build
2. Check disk space (needs 50GB+)
3. Rebuild image if downloads failed

### R2 Upload Fails
**Symptom:** `Error uploading to R2`

**Solutions:**
1. Verify R2 credentials in environment variables
2. Check bucket name and access permissions
3. Ensure R2_PUBLIC_URL is correct

## Cost Optimization

### RunPod Pricing Tips
1. **Use Spot Instances** for development/testing (50-80% cheaper)
2. **Use Secure Cloud** for production (guaranteed availability)
3. **Auto-scale** based on queue depth
4. **Monitor GPU utilization** to avoid idle time

### Recommended Instance Types by Use Case

**Development/Testing:**
- RTX 3090 (24GB) - $0.39/hr spot
- RTX 4090 (24GB) - $0.69/hr spot

**Production (High Volume):**
- RTX A6000 (48GB) - $0.89/hr spot, $1.29/hr secure
- Multiple GPUs with load balancing

**Production (Low Volume):**
- RTX 3090 (24GB) - Sufficient for most workloads
- Scale to A6000 when needed

## Model Files Included

The image includes all required models:
- Wan2_1-InfiniteTalk_Single (2.6GB)
- Wan2_1-InfiniteTalk_Multi (2.6GB)
- wan2.1-i2v-14b-480p-Q8 (10GB)
- lightx2v LoRA (900MB)
- Wan2_1_VAE_bf16 (170MB)
- umt5-xxl-enc-bf16 (5.7GB)
- clip-vit-h-14 (2.5GB)
- MelBand RoFormer (1.2GB)

**Total:** ~26GB of model weights

## Support

For issues or questions:
1. Check logs first: `docker logs -f container_name`
2. Review this guide and DEPLOYMENT_GUIDE.md
3. Check ComfyUI workflows in `/workflows/` directory
4. Verify GPU VRAM requirements are met
