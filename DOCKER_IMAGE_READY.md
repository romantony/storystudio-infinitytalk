# Docker Image Ready for RunPod

## ✅ Image Built Successfully

**Image:** `storystudio/infinitetalk:latest`
**Size:** 102GB
**Base:** PyTorch 2.9.1, CUDA 12.6.3, Python 3.12.3

## 📋 What's Included

### Base Components
- Ubuntu 24.04
- NVIDIA CUDA 12.6.3 + cuDNN 9
- Python 3.12.3
- PyTorch 2.9.1 (CUDA 12.8 compatible)
- ComfyUI with custom nodes

### AI Models (~26GB)
- InfiniteTalk Single & Multi models (2.6GB each)
- Wan2.1 I2V 14B 480P Q8 (10GB)
- Text encoder (umt5-xxl, 5.7GB)
- VAE, CLIP, audio models

### Custom Code
- RunPod handler with automatic job processing
- R2 storage integration
- ComfyUI workflow management
- Video output detection (fixed for VHS nodes)

## 🚀 How to Deploy to RunPod

### Option 1: Push to Docker Hub (Public)

1. **Login to Docker Hub:**
   ```powershell
   docker login
   ```

2. **Run the push script:**
   ```powershell
   .\push_to_dockerhub.ps1
   ```
   
   This will:
   - Tag the image as `storystudio/infinitetalk:latest` and `v1.0`
   - Push both tags to Docker Hub
   - Take 1-3 hours depending on upload speed

3. **Create RunPod Template:**
   - Container Image: `storystudio/infinitetalk:latest`
   - Container Disk: 50GB minimum
   - GPU: RTX 3090 (24GB VRAM) or better
   - Add environment variables (see below)

### Option 2: Private Registry

If you need a private registry:

1. **Tag for your registry:**
   ```powershell
   docker tag storystudio/infinitetalk:latest your-registry.com/infinitetalk:latest
   ```

2. **Push to private registry:**
   ```powershell
   docker push your-registry.com/infinitetalk:latest
   ```

## 🔧 RunPod Configuration

### Environment Variables (Required)

For R2 Storage:
```
R2_ACCOUNT_ID=620baa808df08b1a30d448989365f7dd
R2_BUCKET_NAME=storystudio
R2_ACCESS_KEY_ID=your_access_key_here
R2_SECRET_ACCESS_KEY=your_secret_key_here
R2_PUBLIC_URL=https://parentearn.com
```

### GPU Requirements

⚠️ **IMPORTANT:** This model requires significant VRAM

| GPU | VRAM | Status | Use Case |
|-----|------|--------|----------|
| RTX 3050 | 6GB | ❌ OOM | Not suitable |
| RTX 3090 | 24GB | ✅ Works | Development/Testing |
| RTX 4090 | 24GB | ✅ Works | Production |
| A6000 | 48GB | ✅✅ Best | High-volume production |

### Cost Estimates (RunPod Spot Pricing)

- RTX 3090 (24GB): ~$0.39/hour
- RTX 4090 (24GB): ~$0.69/hour  
- A6000 (48GB): ~$0.89/hour

## 📝 API Request Example

```json
{
  "input": {
    "input_type": "image",
    "person_count": "single",
    "prompt": "A person giving a motivational speech",
    "image_url": "https://example.com/person.jpg",
    "wav_url": "https://example.com/audio.mp3",
    "width": 512,
    "height": 512,
    "max_frame": 60,
    "use_r2_storage": true
  }
}
```

**Note:** Reduce `max_frame` from 150 to 30-60 if using 24GB VRAM GPUs.

## 🎯 Next Steps

1. **Push the image** using `push_to_dockerhub.ps1`
2. **Wait for upload** (1-3 hours for 102GB)
3. **Create RunPod template** with the image
4. **Configure environment variables** for R2
5. **Deploy on 24GB+ VRAM GPU**
6. **Test with API request**

## 📖 Documentation

- Full deployment guide: `RUNPOD_DEPLOYMENT.md`
- Workflow guide: `WORKFLOW_GUIDE.md`
- API examples: `POSTMAN_EXAMPLES.md`
- General deployment: `DEPLOYMENT_GUIDE.md`

## ⚠️ Known Issues

1. **OOM on 6GB GPUs:** The models are too large for 6GB VRAM. Deploy on 24GB+ GPUs.
2. **Long push time:** 102GB takes 1-3 hours to upload.
3. **First run delay:** Initial startup takes 2-3 minutes as models load into VRAM.

## 🆘 Troubleshooting

**OOM Errors:** Deploy on larger GPU or reduce `max_frame` parameter

**ComfyUI not starting:** Check logs, wait 2-3 minutes for startup

**R2 upload fails:** Verify environment variables are set correctly

**Models not found:** Ensure 50GB+ container disk space

## ✨ Features

- ✅ Automatic job processing from test_input.json or RunPod queue
- ✅ R2 storage integration for outputs
- ✅ ComfyUI workflow automation
- ✅ Video output detection (VHS nodes supported)
- ✅ PyTorch 2.9.1 (latest stable)
- ✅ CUDA 12.6 optimized
- ✅ Health checks for RunPod

---

**Ready to deploy to RunPod with 24GB+ VRAM GPUs!** 🚀
