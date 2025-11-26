# Deployment Guide - StoryStudio InfinityTalk

## Prerequisites

- Docker installed with NVIDIA GPU support
- RunPod account with serverless endpoint configured
- Cloudflare R2 account (for storage)
- Python 3.10+

## Step 1: Obtain Workflow JSON Files

The workflow JSON files need to be obtained from the reference repository or exported from ComfyUI:

1. Visit: https://github.com/wlsdml1114/Infinitetalk_Runpod_hub
2. Download the following workflow files:
   - `I2V_single.json` 
   - `I2V_multi.json`
   - `V2V_single.json`
   - `V2V_multi.json`
3. Replace the placeholder files in `models/infinitetalk/workflows/` with the actual workflow JSON files

Alternatively, if you have access to a working InfiniteTalk ComfyUI setup:
- Open ComfyUI and load the InfiniteTalk workflows
- Export each workflow as JSON
- Save them to the appropriate locations

## Step 2: Configure R2 Storage

1. Log into Cloudflare dashboard
2. Navigate to R2 Storage
3. Create a new bucket for your project
4. Generate API credentials:
   - Account ID
   - Access Key ID
   - Secret Access Key
5. Configure public access for the bucket (optional, if you want direct URLs)
6. Copy your public bucket URL (format: `https://your-bucket.r2.dev`)

## Step 3: Build Base Docker Image

```bash
# Navigate to project root
cd c:\runpod\storystudio_infinitytalk

# Build base image
docker build -t storystudio/base:latest -f base/Dockerfile.base .

# Optional: Push to Docker Hub (replace with your registry)
# docker tag storystudio/base:latest yourusername/storystudio-base:latest
# docker push yourusername/storystudio-base:latest
```

## Step 4: Build Model-Specific Image

```bash
# Build InfiniteTalk image
cd models/infinitetalk
docker build -t storystudio/infinitetalk:latest .

# Optional: Push to Docker Hub
# docker tag storystudio/infinitetalk:latest yourusername/infinitetalk:latest
# docker push yourusername/infinitetalk:latest
```

## Step 5: Test Locally with Docker Compose

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` file with your R2 credentials:
```env
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
R2_PUBLIC_URL=https://your-bucket.r2.dev
```

3. Start services:
```bash
docker-compose up
```

4. Test with example client:
```bash
cd examples
python client_example.py
```

## Step 6: Deploy to RunPod

1. Push your Docker image to a registry accessible by RunPod

2. Create a new Serverless Endpoint on RunPod:
   - Go to RunPod Dashboard → Serverless
   - Click "New Endpoint"
   - Configure:
     - **Container Image**: `yourusername/infinitetalk:latest`
     - **Container Disk**: 50 GB minimum
     - **GPU Type**: Select appropriate GPU (A40, A100, etc.)
     - **Min Workers**: 0
     - **Max Workers**: Set based on expected load
     - **Idle Timeout**: 60 seconds
     - **Execution Timeout**: 600 seconds

3. Add Environment Variables:
   ```
   R2_ACCOUNT_ID=your_account_id
   R2_ACCESS_KEY_ID=your_access_key
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_BUCKET_NAME=your_bucket_name
   R2_PUBLIC_URL=https://your-bucket.r2.dev
   ```

4. Optional: Configure Network Volume for persistent storage

## Step 7: Test RunPod Endpoint

Use the example client script:

```python
# Update examples/client_example.py with your endpoint details
RUNPOD_ENDPOINT_ID = "your-endpoint-id"
RUNPOD_API_KEY = "your-api-key"

# Run test
python examples/client_example.py
```

## Step 8: Add More Models

To add a new model:

1. Create new directory under `models/`:
```bash
models/yourmodel/
├── Dockerfile
├── handler.py
├── README.md
├── workflows/
│   └── workflow.json
└── examples/
```

2. Extend `BaseHandler` in your handler:
```python
from base.handler_base import BaseHandler

class YourModelHandler(BaseHandler):
    def get_workflow_path(self, job_input):
        # Return workflow path based on input
        pass
    
    def configure_workflow(self, workflow, job_input, processed_inputs):
        # Configure workflow nodes
        pass
```

3. Create model-specific Dockerfile:
```dockerfile
FROM storystudio/base:latest

# Install model-specific dependencies
RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/your/custom-node

# Download model weights
RUN wget https://huggingface.co/your-model/weights.safetensors \
    -O /ComfyUI/models/checkpoints/your-model.safetensors

COPY handler.py /handler.py
COPY workflows/ /workflows/

CMD ["/entrypoint.sh"]
```

## Monitoring and Logging

### RunPod Dashboard
- Monitor active workers
- View execution logs
- Track GPU usage
- Monitor costs

### CloudWatch/Logging
Set up log aggregation for production:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/handler.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

### Image Build Issues
- Ensure CUDA drivers are compatible
- Check base image availability
- Verify model weight URLs are accessible

### Handler Execution Issues
- Check ComfyUI server is starting correctly
- Verify workflow JSON files are valid
- Check R2 credentials are correct
- Monitor GPU memory usage

### Performance Optimization
- Adjust `max_workers` based on demand
- Use network volumes for frequently accessed data
- Implement caching for model weights
- Use appropriate GPU types for workload

## Cost Optimization

1. **Idle Timeout**: Set to minimum needed (30-60 seconds)
2. **Max Workers**: Don't over-provision
3. **GPU Selection**: Use smallest GPU that meets requirements
4. **Network Volume**: Use for shared data to avoid redownloads
5. **R2 Storage**: Configure lifecycle rules to delete old outputs

## Security Best Practices

1. **API Keys**: Store in environment variables, never in code
2. **R2 Bucket**: 
   - Use signed URLs for sensitive content
   - Configure CORS properly
   - Set appropriate lifecycle policies
3. **RunPod**: 
   - Restrict API key permissions
   - Use network isolation where possible
   - Monitor usage patterns for anomalies

## Support

For issues specific to:
- **Base Framework**: Create issue in this repository
- **InfiniteTalk Model**: See https://github.com/wlsdml1114/Infinitetalk_Runpod_hub
- **RunPod Platform**: Contact RunPod support
- **Cloudflare R2**: Check Cloudflare documentation

## Next Steps

1. Review API documentation in main README.md
2. Explore example client scripts
3. Customize workflows for your use case
4. Set up monitoring and alerting
5. Implement rate limiting and usage tracking
