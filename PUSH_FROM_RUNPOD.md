# Push Docker Image from RunPod Instance

## Overview
This guide shows how to use a RunPod GPU instance to build and push your 102GB InfiniteTalk Docker image to Docker Hub. RunPod instances have fast upload speeds, making this much more reliable than pushing from home internet.

**Time Required:** 1-2 hours  
**Cost:** ~$0.80 (2 hours × $0.40/hr for RTX 3090)

---

## Step 1: Deploy a RunPod Instance

### 1.1 Go to RunPod
Visit: https://www.runpod.io/console/pods

### 1.2 Create New Pod
- Click **"+ Deploy"** or **"GPU Pod"**
- Select **"Community Cloud"** (cheaper)

### 1.3 Choose GPU
Any GPU works for building (no need for 24GB):
- **RTX 3090** - $0.40/hr (recommended)
- **RTX 3080** - $0.35/hr
- **RTX 4070** - $0.35/hr

### 1.4 Configure Pod
- **Template:** Select **"RunPod Pytorch"** or **"RunPod Ubuntu"**
- **Container Disk:** 150GB (need space for 102GB image)
- **Volume:** Not needed
- **Expose Ports:** Enable TCP 22 (SSH)

### 1.5 Deploy
- Click **"Deploy On-Demand"**
- Wait 1-2 minutes for pod to start

---

## Step 2: Connect to Pod via SSH

### 2.1 Get SSH Connection Details
In RunPod dashboard:
- Click on your pod
- Find **"Connection"** section
- Copy the SSH command (looks like):
  ```
  ssh root@X.X.X.X -p XXXXX -i ~/.ssh/id_ed25519
  ```

### 2.2 Connect
**On Windows (PowerShell):**
```powershell
# If you don't have SSH key, use password from RunPod dashboard
ssh root@X.X.X.X -p XXXXX
```

**On Linux/Mac:**
```bash
ssh root@X.X.X.X -p XXXXX
```

When prompted, type `yes` to accept fingerprint.

---

## Step 3: Install Docker on Pod

Once connected to the pod:

```bash
# Update package lists
apt-get update

# Install Docker (if not already installed)
apt-get install -y docker.io

# Start Docker service
service docker start

# Verify Docker is working
docker --version
```

Expected output: `Docker version 24.x.x` or similar

---

## Step 4: Transfer Your Built Image to RunPod

You have **3 options** to get your image to RunPod:

### Option A: Save and Transfer (RECOMMENDED - Fastest)

**On your local machine (Windows PowerShell):**

```powershell
# Save image to tar file
docker save storystudio/infinitetalk:latest -o infinitetalk.tar

# Compress it (optional, saves upload time)
# This will take 10-20 minutes but reduces file to ~50GB
tar -czf infinitetalk.tar.gz infinitetalk.tar

# Upload to RunPod (replace X.X.X.X and port)
scp -P XXXXX infinitetalk.tar.gz root@X.X.X.X:/root/

# Alternative: Use WinSCP GUI on Windows
# Download WinSCP: https://winscp.net
# Protocol: SCP
# Host: X.X.X.X
# Port: XXXXX
# Username: root
# Transfer infinitetalk.tar.gz
```

**On RunPod SSH session:**

```bash
# Load the image
docker load -i /root/infinitetalk.tar.gz
# OR if you didn't compress:
docker load -i /root/infinitetalk.tar

# Verify image loaded
docker images storystudio/infinitetalk
```

### Option B: Build on RunPod (Alternative)

**On RunPod SSH session:**

```bash
# Install git
apt-get install -y git

# Clone your repository
git clone https://github.com/romantony/storystudio-infinitytalk.git
cd storystudio-infinitytalk

# Build base image (takes ~20 minutes)
docker build -t storystudio/base:latest -f base/Dockerfile.base .

# Build InfiniteTalk image (takes ~40 minutes)
docker build -t storystudio/infinitetalk:latest -f models/infinitetalk/Dockerfile models/infinitetalk
```

### Option C: Use Docker Hub as Intermediate (If image was partially pushed)

```bash
# Pull your partially completed image (won't work if manifest doesn't exist)
docker pull romantony/storystudio-infinitetalk:latest
```

---

## Step 5: Tag and Push to Docker Hub

**On RunPod SSH session:**

```bash
# Login to Docker Hub
docker login
# Enter username: romantony
# Enter password: (your Docker Hub password or access token)

# Tag the image
docker tag storystudio/infinitetalk:latest romantony/storystudio-infinitetalk:latest
docker tag storystudio/infinitetalk:latest romantony/storystudio-infinitetalk:v1.0

# Push to Docker Hub (this will be FAST from RunPod - 20-40 minutes)
docker push romantony/storystudio-infinitetalk:latest
docker push romantony/storystudio-infinitetalk:v1.0
```

**Monitor progress:**
```bash
# In another terminal, watch Docker stats
docker system df -v
```

Expected output while pushing:
```
The push refers to repository [docker.io/romantony/storystudio-infinitetalk]
...
bb765a456f0e: Pushing [==============>                    ] 5.2GB/17.6GB
89507e62875d: Pushing [======>                            ] 2.1GB/8.91GB
...
```

**✅ Success looks like:**
```
latest: digest: sha256:abc123... size: 15234
```

---

## Step 6: Verify Push Succeeded

**On your local machine or in RunPod:**

```bash
# Check manifest exists
docker manifest inspect romantony/storystudio-infinitetalk:latest

# Should show image details with layers
```

**Or visit Docker Hub:**
https://hub.docker.com/r/romantony/storystudio-infinitetalk/tags

You should see `latest` and `v1.0` tags listed.

---

## Step 7: Terminate RunPod Instance

**Important:** Don't forget to stop the pod to avoid charges!

1. Go to RunPod dashboard
2. Click on your pod
3. Click **"Terminate"**
4. Confirm termination

**Cost Summary:**
- Upload time: ~30 minutes
- Build time (if building): ~60 minutes  
- Push time: ~30 minutes
- **Total:** ~2 hours = **$0.80**

---

## Step 8: Deploy on RunPod Serverless

Now that your image is on Docker Hub, follow the deployment guide:

See: `RUNPOD_DEPLOYMENT.md`

Quick setup:
1. Go to https://www.runpod.io/console/serverless
2. Click **"+ New Template"**
3. **Container Image:** `romantony/storystudio-infinitetalk:latest`
4. **Container Disk:** 50GB
5. **Environment Variables:** Add R2 credentials
6. **GPU Types:** Select RTX 3090 (24GB) or better
7. Click **"Save Template"**
8. Create new endpoint using this template

---

## Troubleshooting

### SSH Connection Refused
- Make sure pod is fully started (status: Running)
- Check that TCP port 22 is exposed
- Verify you're using correct IP and port from RunPod dashboard

### Docker Not Found
```bash
apt-get update && apt-get install -y docker.io
service docker start
```

### Out of Disk Space
```bash
# Check space
df -h

# Clean up if needed
docker system prune -a

# If still not enough, recreate pod with larger container disk
```

### Push Still Timing Out (Unlikely from RunPod)
```bash
# Check RunPod network status
ping 8.8.8.8

# If network issues persist, try different RunPod datacenter
# Terminate pod and create new one in different region
```

### Image Load Failed
```bash
# Verify tar file integrity
ls -lh infinitetalk.tar.gz

# Try loading uncompressed version
gunzip infinitetalk.tar.gz
docker load -i infinitetalk.tar
```

---

## Alternative: Upload Compressed Image to Cloud Storage

If transfer to RunPod is slow, use intermediate cloud storage:

### Using Dropbox/Google Drive

**On local machine:**
```powershell
# Save and compress
docker save storystudio/infinitetalk:latest | gzip > infinitetalk.tar.gz

# Upload to Dropbox/Google Drive via web browser
```

**On RunPod:**
```bash
# Download from cloud storage
wget "https://dropbox.com/...share_link.../infinitetalk.tar.gz" -O infinitetalk.tar.gz

# Load image
docker load -i infinitetalk.tar.gz
```

### Using AWS S3 (If you have AWS account)

**On local machine:**
```powershell
# Install AWS CLI
# Upload to S3
aws s3 cp infinitetalk.tar.gz s3://your-bucket/infinitetalk.tar.gz
```

**On RunPod:**
```bash
# Install AWS CLI
apt-get install -y awscli

# Download from S3
aws s3 cp s3://your-bucket/infinitetalk.tar.gz .

# Load image
docker load -i infinitetalk.tar.gz
```

---

## Summary

✅ **What This Achieves:**
- Image successfully pushed to Docker Hub
- Ready for RunPod serverless deployment
- Avoids home internet upload limitations

✅ **Cost:**
- One-time: ~$0.80 (2 hours RunPod instance)
- Docker Hub: Free (public image)

✅ **Next Steps:**
1. Follow this guide to push image
2. Once pushed, use `RUNPOD_DEPLOYMENT.md` to create serverless endpoint
3. Test with sample request
4. Deploy in production

---

## Quick Command Reference

```bash
# On RunPod Instance
apt-get update && apt-get install -y docker.io
service docker start
docker load -i infinitetalk.tar.gz
docker login
docker tag storystudio/infinitetalk:latest romantony/storystudio-infinitetalk:latest
docker push romantony/storystudio-infinitetalk:latest
# Wait for push to complete (~30 mins)
# Verify: docker manifest inspect romantony/storystudio-infinitetalk:latest
# Terminate pod in RunPod dashboard
```

---

**Ready to proceed?** Start with Step 1 and follow each step in order.
