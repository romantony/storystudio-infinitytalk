# Build and Push Docker Image from RunPod (Build from Scratch)

## Overview
Build your InfiniteTalk Docker image directly on a RunPod instance and push to Docker Hub. This avoids transferring the 102GB image and leverages RunPod's fast network.

**Time Required:** 1.5-2 hours  
**Cost:** ~$0.80-$1.00 (2-2.5 hours × $0.40/hr)

---

## Step 1: Deploy RunPod Instance

### 1.1 Go to RunPod Console
Visit: https://www.runpod.io/console/pods

### 1.2 Deploy New Pod
- Click **"+ Deploy"** → **"GPU Pod"**
- Select **"Community Cloud"** (cheaper than Secure Cloud)

### 1.3 Select GPU
Any GPU works for building:
- **RTX 3090** - $0.40/hr ✅ (recommended)
- **RTX 3080** - $0.35/hr
- **RTX 4070** - $0.35/hr

### 1.4 Choose Template
- Select **"RunPod Pytorch"** or **"RunPod Ubuntu"**
- Both include Docker pre-installed

### 1.5 Configure Storage
- **Container Disk:** 150GB (need space for building 102GB image)
- **Volume:** Not needed

### 1.6 Expose SSH
- **Expose TCP Ports:** Check port 22 (SSH)

### 1.7 Deploy
- Click **"Deploy On-Demand"**
- Wait 1-2 minutes for pod to start (status: Running)

---

## Step 2: Connect via SSH

### 2.1 Get Connection Command
In RunPod dashboard:
- Click on your running pod
- Find **"Connection"** section
- Copy the SSH command, looks like:
  ```
  ssh root@123.45.67.89 -p 12345
  ```

### 2.2 Connect from Your Computer

**Windows PowerShell:**
```powershell
ssh root@123.45.67.89 -p 12345
```

**Linux/Mac Terminal:**
```bash
ssh root@123.45.67.89 -p 12345
```

Type `yes` when prompted to accept the fingerprint.

---

## Step 3: Prepare Build Environment

Once connected to RunPod:

```bash
# Update system
apt-get update

# Install required tools
apt-get install -y git docker.io wget curl

# Start Docker service (if not running)
service docker start

# Verify Docker
docker --version
# Should show: Docker version 24.x.x or similar

# Check available disk space
df -h /
# Should have ~140GB available
```

---

## Step 4: Clone Your Repository

```bash
# Navigate to workspace
cd /workspace

# Clone your repository
git clone https://github.com/romantony/storystudio-infinitytalk.git

# Enter the directory
cd storystudio-infinitytalk

# Verify files
ls -la
# Should see: base/, models/, docker-compose.yml, etc.
```

---

## Step 5: Build Base Image

```bash
# Build the base image
docker build -t storystudio/base:latest -f base/Dockerfile.base .
```

**Expected build time:** 20-30 minutes

**Build progress will show:**
```
[1/15] FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
[2/15] RUN apt-get update && apt-get install -y ...
[3/15] RUN wget https://www.python.org/ftp/python/3.12.3/...
...
[15/15] RUN pip install torch==2.9.1 torchvision==0.24.1 ...
```

**✅ Success looks like:**
```
Successfully built abc123def456
Successfully tagged storystudio/base:latest
```

**Verify base image:**
```bash
docker images storystudio/base
```

---

## Step 6: Build InfiniteTalk Image

```bash
# Build InfiniteTalk with all models
docker build -t storystudio/infinitetalk:latest -f models/infinitetalk/Dockerfile models/infinitetalk
```

**Expected build time:** 40-60 minutes

**Build progress will show:**
```
[1/22] FROM storystudio/base:latest
[2/22] RUN apt-get update && apt-get install -y ...
[3/22] RUN cd /ComfyUI/custom_nodes && git clone ...
...
[10/22] RUN wget https://huggingface.co/.../wan2.1-i2v-14b-480p-Q8_0.gguf ...
[11/22] RUN wget https://huggingface.co/.../umt5-xxl-fp16.safetensors ...
...
[22/22] CMD ["python", "-u", "handler.py"]
```

**✅ Success looks like:**
```
Successfully built xyz789abc123
Successfully tagged storystudio/infinitetalk:latest
```

**Verify final image:**
```bash
docker images storystudio/infinitetalk

# Check size (should be ~102GB)
```

---

## Step 7: Login to Docker Hub

```bash
# Login to Docker Hub
docker login

# Enter your credentials:
# Username: romantony
# Password: (your Docker Hub password or access token)
```

**✅ Success looks like:**
```
Login Succeeded
```

---

## Step 8: Tag and Push to Docker Hub

```bash
# Tag the image with your Docker Hub username
docker tag storystudio/infinitetalk:latest romantony/storystudio-infinitetalk:latest
docker tag storystudio/infinitetalk:latest romantony/storystudio-infinitetalk:v1.0

# Push to Docker Hub (FAST from RunPod - 20-40 minutes)
docker push romantony/storystudio-infinitetalk:latest
docker push romantony/storystudio-infinitetalk:v1.0
```

**Push progress:**
```
The push refers to repository [docker.io/romantony/storystudio-infinitetalk]
bb765a456f0e: Pushing [========>                          ] 3.2GB/17.6GB
89507e62875d: Pushing [=====>                             ] 1.5GB/8.91GB
39666a7c8c60: Pushing [===========>                       ] 1.2GB/2.59GB
...
```

**✅ Success looks like:**
```
latest: digest: sha256:abc123def456... size: 15234
v1.0: digest: sha256:abc123def456... size: 15234
```

---

## Step 9: Verify Push Succeeded

```bash
# Check the manifest exists
docker manifest inspect romantony/storystudio-infinitetalk:latest
```

**Expected output:**
```json
{
   "schemaVersion": 2,
   "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
   "config": {
      "mediaType": "application/vnd.docker.container.image.v1+json",
      "size": 123456,
      "digest": "sha256:abc123..."
   },
   "layers": [
      ...
   ]
}
```

**Also verify on Docker Hub web:**
https://hub.docker.com/r/romantony/storystudio-infinitetalk/tags

---

## Step 10: Clean Up and Terminate Pod

```bash
# Optional: Clean up to free space
docker system prune -a

# Exit SSH
exit
```

**In RunPod Dashboard:**
1. Go to https://www.runpod.io/console/pods
2. Click on your pod
3. Click **"Terminate"** button
4. Confirm termination

**✅ Don't forget this step to avoid ongoing charges!**

---

## Time and Cost Breakdown

| Step | Time | Notes |
|------|------|-------|
| Deploy Pod | 2 min | Instance startup |
| Install Tools | 5 min | Git, Docker setup |
| Clone Repo | 2 min | Small repository |
| Build Base | 25 min | PyTorch installation |
| Build InfiniteTalk | 50 min | Model downloads |
| Push to Docker Hub | 30 min | Fast upload |
| **Total** | **~2 hours** | **$0.80 @ $0.40/hr** |

---

## Troubleshooting

### Build Fails - Out of Disk Space
```bash
# Check space
df -h

# Clean Docker cache
docker system prune -a

# If still insufficient, terminate and recreate pod with 200GB disk
```

### Build Fails - Network Issues Downloading Models
```bash
# Retry the build command
docker build -t storystudio/infinitetalk:latest -f models/infinitetalk/Dockerfile models/infinitetalk

# Docker will cache successful layers and resume from failure point
```

### Hugging Face Download 403 Forbidden
```bash
# Temporary URL expiration - just retry the build
docker build -t storystudio/infinitetalk:latest -f models/infinitetalk/Dockerfile models/infinitetalk
```

### Push Fails - Still Timing Out (Unlikely)
```bash
# Check RunPod network
ping 8.8.8.8

# Check Docker daemon
service docker status

# Restart Docker if needed
service docker restart
docker login
docker push romantony/storystudio-infinitetalk:latest
```

### Can't Connect via SSH
- Verify pod status is "Running"
- Check TCP port 22 is exposed in pod settings
- Try reconnecting after 1-2 minutes
- If persistent, terminate and create new pod

---

## What's Next?

Once the image is successfully pushed to Docker Hub:

### 1. Deploy on RunPod Serverless
Follow the guide: **`RUNPOD_DEPLOYMENT.md`**

Quick steps:
```bash
# In RunPod Console:
1. Go to Serverless → Templates
2. Create New Template
3. Image: romantony/storystudio-infinitetalk:latest
4. Container Disk: 50GB
5. Environment Variables: Add R2 credentials
6. GPU: Select RTX 3090 (24GB) or better
7. Save and create endpoint
```

### 2. Test the Deployment
```python
import requests

endpoint_url = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"
api_key = "your_runpod_api_key"

response = requests.post(
    endpoint_url,
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "input": {
            "workflow": "I2V_single",
            "reference_image_url": "https://your-image.jpg",
            "audio_url": "https://your-audio.mp3",
            "max_frame": 90
        }
    }
)

print(response.json())
```

### 3. Monitor Costs
- RunPod Serverless charges per second of GPU usage
- Only pay when inference is running
- Typical I2V_single: 2-5 minutes @ $0.40/hr = $0.01-$0.03 per video

---

## Quick Command Reference Sheet

Save this for quick copy-paste:

```bash
# On RunPod Instance
cd /workspace
git clone https://github.com/romantony/storystudio-infinitytalk.git
cd storystudio-infinitytalk

# Build images
docker build -t storystudio/base:latest -f base/Dockerfile.base .
docker build -t storystudio/infinitetalk:latest -f models/infinitetalk/Dockerfile models/infinitetalk

# Tag and push
docker login
docker tag storystudio/infinitetalk:latest romantony/storystudio-infinitetalk:latest
docker tag storystudio/infinitetalk:latest romantony/storystudio-infinitetalk:v1.0
docker push romantony/storystudio-infinitetalk:latest
docker push romantony/storystudio-infinitetalk:v1.0

# Verify
docker manifest inspect romantony/storystudio-infinitetalk:latest

# Clean up (in RunPod dashboard)
# Terminate pod to stop charges
```

---

## Ready to Start?

Follow the steps in order:
1. ✅ Deploy RunPod instance (Step 1)
2. ✅ Connect via SSH (Step 2)
3. ✅ Clone repository (Step 4)
4. ✅ Build images (Steps 5-6)
5. ✅ Push to Docker Hub (Steps 7-8)
6. ✅ Terminate pod (Step 10)

**Total time:** ~2 hours  
**Total cost:** ~$0.80
