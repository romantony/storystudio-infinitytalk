# StoryStudio Multi-Model RunPod Serverless

A flexible framework for deploying multiple AI models on RunPod Serverless with Cloudflare R2 storage integration. This repository provides a modular structure to host different models (video generation, image-to-video, text-to-video, etc.) on RunPod serverless infrastructure.

## 🎯 Features

- **Multi-Model Support**: Modular structure to host multiple AI models
- **RunPod Serverless**: Optimized for serverless deployment with automatic scaling
- **R2 Storage Integration**: Automatic upload of generated assets to Cloudflare R2
- **ComfyUI Based**: Leverages ComfyUI for flexible workflow management
- **Flexible Input**: Supports URL, local paths, and Base64 encoded inputs
- **Network Volume Support**: Handle large files efficiently with RunPod Network Volumes

## 📁 Project Structure

```
storystudio_infinitytalk/
├── base/                          # Base templates and utilities
│   ├── Dockerfile.base            # Base Docker image with common dependencies
│   ├── handler_base.py            # Base handler class with common functionality
│   ├── entrypoint.sh              # Generic entrypoint script
│   └── utils/                     # Shared utilities
│       ├── r2_storage.py          # R2 storage integration
│       ├── input_processor.py     # Input processing (URL/path/base64)
│       └── comfyui_client.py      # ComfyUI websocket client
├── models/                        # Individual model implementations
│   ├── infinitetalk/              # InfiniteTalk model
│   │   ├── Dockerfile             # Model-specific Dockerfile
│   │   ├── handler.py             # Model-specific handler
│   │   ├── workflows/             # ComfyUI workflow files
│   │   │   ├── I2V_single.json
│   │   │   ├── I2V_multi.json
│   │   │   ├── V2V_single.json
│   │   │   └── V2V_multi.json
│   │   └── README.md              # Model-specific documentation
│   └── [other_models]/            # Additional models...
├── examples/                      # Example files for testing
│   ├── image.jpg
│   └── audio.mp3
└── docker-compose.yml             # Local testing setup
```

## 🚀 Quick Start

### Prerequisites

- Docker
- RunPod account
- Cloudflare R2 account (for storage integration)

### Local Testing

```bash
# Clone the repository
git clone <repository-url>
cd storystudio_infinitytalk

# Build and run a specific model locally
cd models/infinitetalk
docker build -t infinitetalk:latest .
docker run -p 8188:8188 infinitetalk:latest
```

### Deploy to RunPod

1. **Build and Push Docker Image**:
```bash
docker build -t your-dockerhub-username/infinitetalk:latest .
docker push your-dockerhub-username/infinitetalk:latest
```

2. **Create RunPod Serverless Endpoint**:
   - Go to RunPod Serverless
   - Create new endpoint
   - Use your Docker image
   - Configure environment variables (R2 credentials)

3. **Test the Endpoint**:
```python
import requests

endpoint_url = "https://api.runpod.ai/v2/your-endpoint-id/runsync"
headers = {
    "Authorization": "Bearer YOUR_RUNPOD_API_KEY"
}

payload = {
    "input": {
        "input_type": "image",
        "person_count": "single",
        "prompt": "A person talking naturally",
        "image_url": "https://example.com/portrait.jpg",
        "wav_url": "https://example.com/audio.wav",
        "width": 512,
        "height": 512,
        "use_r2_storage": True
    }
}

response = requests.post(endpoint_url, json=payload, headers=headers)
print(response.json())
```

## 🔧 Configuration

### Environment Variables

Set these environment variables in your RunPod endpoint configuration:

```bash
# R2 Storage Configuration
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
R2_PUBLIC_URL=https://your-bucket.r2.dev

# Optional: Network Volume
NETWORK_VOLUME_PATH=/runpod-volume
```

### R2 Storage Setup

1. Create a Cloudflare R2 bucket
2. Generate API tokens with read/write permissions
3. Configure public access settings
4. Add credentials to RunPod endpoint environment variables

## 📝 API Reference

### Input Parameters

#### Common Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_type` | string | No | "image" | Input type: "image" or "video" |
| `prompt` | string | No | "A person talking naturally" | Description for generation |
| `width` | integer | No | 512 | Output width in pixels |
| `height` | integer | No | 512 | Output height in pixels |
| `use_r2_storage` | boolean | No | false | Upload output to R2 and return URL |
| `network_volume` | boolean | No | false | Use network volume for large files |

#### Input Methods (choose one)
- **URL**: `image_url`, `video_url`, `wav_url`
- **Path**: `image_path`, `video_path`, `wav_path` (for network volume)
- **Base64**: `image_base64`, `video_base64`, `wav_base64`

### Output Formats

#### With R2 Storage (`use_r2_storage: true`)
```json
{
  "status": "success",
  "r2_url": "https://your-bucket.r2.dev/output/video_12345.mp4",
  "file_size": 1024576,
  "duration": 10.5
}
```

#### With Network Volume (`network_volume: true`)
```json
{
  "status": "success",
  "video_path": "/runpod-volume/output_12345.mp4"
}
```

#### Base64 Output (default)
```json
{
  "status": "success",
  "video": "data:video/mp4;base64,..."
}
```

## 🔨 Adding New Models

To add a new model to the framework:

1. **Create Model Directory**:
```bash
mkdir -p models/your_model/{workflows}
```

2. **Create Dockerfile**:
```dockerfile
FROM storystudio/base:latest

# Install model-specific dependencies
RUN pip install your-model-requirements

# Download model weights
RUN huggingface-cli download model-name --local-dir /models/your_model

# Copy workflow files
COPY workflows/ /workflows/

# Copy handler
COPY handler.py /handler.py
```

3. **Implement Handler**:
```python
from base.handler_base import BaseHandler

class YourModelHandler(BaseHandler):
    def get_workflow_path(self, input_params):
        # Return appropriate workflow file
        pass
    
    def process_result(self, output_path):
        # Process and return results
        pass
```

4. **Test and Deploy**:
```bash
cd models/your_model
docker build -t your_model:latest .
docker push your-dockerhub-username/your_model:latest
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [RunPod](https://runpod.io/) - Serverless GPU infrastructure
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Workflow management
- [Cloudflare R2](https://www.cloudflare.com/products/r2/) - Object storage
- [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) - Reference implementation

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the model-specific README files
- Review the API documentation

---

**Built with ❤️ for the AI community**
