# Build and Push Docker Image from Cloud (Build from Scratch)

## Overview
Build your InfiniteTalk Docker image on a cloud instance and push to Docker Hub. This avoids transferring the 40GB image and leverages cloud providers' fast network.

**Recommended: AWS EC2** (Full Docker support, no restrictions)  
**Alternative: RunPod** (Cheaper but Docker needs workarounds)

**Time Required:** 1.5-2 hours  
**Cost:** 
- **EC2 g5.xlarge:** ~$2.00 (2 hours × $1.01/hr)
- **RunPod RTX 3090:** ~$0.80 (2 hours × $0.40/hr)

---

## Option A: AWS EC2 (Recommended)

### Step 1: Launch EC2 Instance

#### 1.1 Go to EC2 Console
Visit: https://console.aws.amazon.com/ec2/

#### 1.2 Launch Instance
- Click **"Launch Instance"**
- Name: `docker-build-infinitetalk`

#### 1.3 Choose AMI
- **Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)**
- Has Docker, NVIDIA drivers pre-installed

#### 1.4 Choose Instance Type
- **g5.xlarge** (24GB GPU, 4 vCPU, 16GB RAM) - $1.01/hr ✅
- Or **g4dn.xlarge** (16GB GPU) - $0.53/hr (slower)

#### 1.5 Key Pair
- Create new or use existing key pair for SSH access
- Download `.pem` file if creating new

#### 1.6 Storage
- **200 GB gp3** (need space for 40GB image)

#### 1.7 Security Group
- Allow **SSH (22)** from your IP
- Allow **HTTP (80)** and **HTTPS (443)** for Docker Hub

#### 1.8 Launch
- Click **"Launch Instance"**
- Wait 2-3 minutes for status: Running

### Step 2: Connect via SSH

#### 2.1 Get Public IP
From EC2 Console → Instances → Select your instance → Copy **Public IPv4 address**

#### 2.2 Connect

**Windows (PowerShell):**
```powershell
ssh -i "your-key.pem" ubuntu@<EC2-PUBLIC-IP>
```

**Linux/Mac:**
```bash
chmod 400 your-key.pem
ssh -i "your-key.pem" ubuntu@<EC2-PUBLIC-IP>
```

### Step 3: Prepare Build Environment

```bash
# Update system
sudo apt-get update

# Verify Docker is installed
docker --version
# Should show: Docker version 20.x or higher

# Verify GPU is accessible
nvidia-smi
# Should show your GPU (A10G on g5.xlarge)

# Check disk space
df -h /
# Should have ~190GB available
```

### Step 4: Clone Repository

```bash
# Clone your repository
cd ~
git clone https://github.com/romantony/storystudio-infinitytalk.git
cd storystudio-infinitytalk
```

### Step 5: Build Image (Single Combined Build)

```bash
# Build using the root Dockerfile (combined approach - simpler!)
docker build -t romantony/storystudio-infinitetalk:latest .
```

**Build time:** 60-90 minutes  
**Progress shows:** CUDA install → PyTorch → ComfyUI → Model downloads

### Step 6: Push to Docker Hub

```bash
# Login
docker login
# Username: romantony
# Password: <your-docker-hub-token>

# Push
docker push romantony/storystudio-infinitetalk:latest
```

**Push time:** 20-30 minutes from EC2

### Step 7: Clean Up

```bash
# Exit SSH
exit
```

**In EC2 Console:**
- Select instance → **Actions** → **Instance State** → **Terminate**

**✅ Don't forget to terminate to stop charges!**

---

## Option B: RunPod Instance

### Step 1: Deploy RunPod Instance

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
- Select **"RunPod Pytorch"** template
- Has Docker pre-installed

### 1.5 Configure Storage
- **Container Disk:** 200GB (need space for building 40GB image)
- **Volume:** Not needed

### 1.6 Expose SSH
- **Expose TCP Ports:** Check port 22 (SSH)

### 1.7 Deploy
- Click **"Deploy On-Demand"**
- Wait 1-2 minutes for pod to start (status: Running)

---

### Step 2: Connect via SSH (RunPod)

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

### Step 3: Prepare Build Environment (RunPod)

Once connected to RunPod:

```bash
# Update system
apt-get update

# Install required tools (if not already installed)
apt-get install -y git wget curl

# Start Docker with iptables disabled (RunPod workaround)
pkill dockerd 2>/dev/null
dockerd --iptables=false --ip-masq=false > /tmp/dockerd.log 2>&1 &
sleep 10

# Verify Docker is working
docker info
# Should show Docker daemon info without errors

# Check available disk space
df -h /
# Should have ~190GB available
```

---

### Step 4: Clone Repository (RunPod)

```bash
# Navigate to workspace
cd /workspace

# Clone your repository
git clone https://github.com/romantony/storystudio-infinitytalk.git

# Enter the directory
cd storystudio-infinitytalk

# Verify files
ls -la
# Should see: Dockerfile, base/, models/, etc.
```

---

### Step 5: Build Image (RunPod - Use Combined Build)

```bash
# Build using root Dockerfile (simpler, no two-stage complexity)
docker build -t romantony/storystudio-infinitetalk:latest .
```

**Expected build time:** 60-90 minutes  
**Downloads:** 23GB of model weights

---

### Step 6: Push to Docker Hub (RunPod)

```bash
# Login to Docker Hub
docker login
# Username: romantony
# Password: <your-docker-hub-token>

# Push image
docker push romantony/storystudio-infinitetalk:latest
```

**Push time:** 20-40 minutes from RunPod

---

### Step 7: Clean Up (RunPod)

```bash
# Exit SSH
exit
```

**In RunPod Dashboard:**
- Terminate pod to stop charges

---

## Comparison: EC2 vs RunPod

| Feature | AWS EC2 | RunPod |
|---------|---------|--------|
| **Cost** | $2.00 (2hr) | $0.80 (2hr) |
| **Docker** | ✅ Full support | ⚠️ Needs workarounds |
| **Network** | Fast (AWS) | Very fast |
| **Setup** | Simple | Moderate |
| **Best for** | Production builds | Budget builds |

**Recommendation:** Use **EC2** for reliability, **RunPod** for cost savings.

---

## Step 8: Verify Push Succeeded

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

## Time and Cost Breakdown

### EC2 g5.xlarge
| Step | Time | Cost |
|------|------|------|
| Launch + Setup | 5 min | $0.08 |
| Build Image | 75 min | $1.26 |
| Push to Hub | 25 min | $0.42 |
| **Total** | **105 min** | **~$1.76** |

### RunPod RTX 3090
| Step | Time | Cost |
|------|------|------|
| Deploy + Setup | 10 min | $0.07 |
| Build Image | 75 min | $0.50 |
| Push to Hub | 30 min | $0.20 |
| **Total** | **115 min** | **~$0.77** |

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
docker info

# Restart Docker if needed
pkill dockerd
dockerd > /dev/null 2>&1 &
sleep 5
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

## Quick Command Reference

### EC2 (Recommended)
```bash
# On EC2 instance
git clone https://github.com/romantony/storystudio-infinitytalk.git
cd storystudio-infinitytalk
docker build -t romantony/storystudio-infinitetalk:latest .
docker login
docker push romantony/storystudio-infinitetalk:latest
# Then terminate EC2 instance
```

### RunPod (Budget)
```bash
# On RunPod instance
pkill dockerd; dockerd --iptables=false > /tmp/dockerd.log 2>&1 &
sleep 10
cd /workspace
git clone https://github.com/romantony/storystudio-infinitytalk.git
cd storystudio-infinitytalk
docker build -t romantony/storystudio-infinitetalk:latest .
docker login
docker push romantony/storystudio-infinitetalk:latest
# Then terminate RunPod pod
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
