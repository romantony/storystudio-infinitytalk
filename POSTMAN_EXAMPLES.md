# Postman / cURL Testing Examples

This document provides complete cURL request examples for testing the InfiniteTalk RunPod Serverless API.

## Prerequisites

1. **RunPod Endpoint**: Deploy your Docker image to RunPod Serverless
2. **API Key**: Get your RunPod API key from the dashboard
3. **Endpoint ID**: Note your endpoint ID after deployment

Replace these variables in the examples below:
- `YOUR_ENDPOINT_ID` - Your RunPod endpoint ID
- `YOUR_RUNPOD_API_KEY` - Your RunPod API key

---

## 1. Image-to-Video Single Person (I2V Single)

### Using URL Inputs

```bash
curl --request POST \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": {
      "input_type": "image",
      "person_count": "single",
      "prompt": "A person talking naturally",
      "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=512&h=512&fit=crop",
      "wav_url": "https://example.com/audio.wav",
      "width": 512,
      "height": 512,
      "use_r2_storage": true
    }
  }'
```

### Using Base64 Inputs

```bash
curl --request POST \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": {
      "input_type": "image",
      "person_count": "single",
      "prompt": "A person talking naturally",
      "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
      "wav_base64": "data:audio/wav;base64,UklGRiQAAABXQVZF...",
      "width": 512,
      "height": 512,
      "use_r2_storage": false
    }
  }'
```

### Using Local Paths (for Network Volume)

```bash
curl --request POST \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": {
      "input_type": "image",
      "person_count": "single",
      "prompt": "A person talking naturally",
      "image_path": "/runpod-volume/images/portrait.jpg",
      "wav_path": "/runpod-volume/audio/speech.wav",
      "width": 512,
      "height": 512,
      "network_volume": true
    }
  }'
```

---

## 2. Image-to-Video Multiple People (I2V Multi)

```bash
curl --request POST \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": {
      "input_type": "image",
      "person_count": "multi",
      "prompt": "Two people having a conversation",
      "image_url": "https://example.com/group-portrait.jpg",
      "wav_url": "https://example.com/audio1.wav",
      "wav_url_2": "https://example.com/audio2.wav",
      "width": 512,
      "height": 512,
      "use_r2_storage": true
    }
  }'
```

---

## 3. Video-to-Video Single Person (V2V Single)

```bash
curl --request POST \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": {
      "input_type": "video",
      "person_count": "single",
      "prompt": "A person talking in a video",
      "video_url": "https://example.com/input-video.mp4",
      "wav_url": "https://example.com/new-audio.wav",
      "width": 512,
      "height": 512,
      "use_r2_storage": true
    }
  }'
```

---

## 4. Video-to-Video Multiple People (V2V Multi)

```bash
curl --request POST \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": {
      "input_type": "video",
      "person_count": "multi",
      "prompt": "Two people talking in a video",
      "video_url": "https://example.com/input-video.mp4",
      "wav_url": "https://example.com/audio1.wav",
      "wav_url_2": "https://example.com/audio2.wav",
      "width": 512,
      "height": 512,
      "max_frame": 200,
      "use_r2_storage": true
    }
  }'
```

---

## 5. Async Request (for longer jobs)

### Submit Job

```bash
curl --request POST \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "input": {
      "input_type": "image",
      "person_count": "single",
      "prompt": "A person talking naturally",
      "image_url": "https://example.com/portrait.jpg",
      "wav_url": "https://example.com/audio.wav",
      "width": 512,
      "height": 512,
      "use_r2_storage": true
    }
  }'
```

Response:
```json
{
  "id": "your-job-id-here",
  "status": "IN_QUEUE"
}
```

### Check Job Status

```bash
curl --request GET \
  --url https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/your-job-id-here \
  --header 'Authorization: Bearer YOUR_RUNPOD_API_KEY'
```

---

## Input Parameters Reference

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_type` | string | `"image"` for I2V or `"video"` for V2V |
| `person_count` | string | `"single"` or `"multi"` |

### Media Input (choose one per type)

**Image Input:**
- `image_path` - Local file path
- `image_url` - HTTP/HTTPS URL
- `image_base64` - Base64 encoded string

**Video Input:**
- `video_path` - Local file path
- `video_url` - HTTP/HTTPS URL
- `video_base64` - Base64 encoded string

**Audio Input (primary):**
- `wav_path` - Local file path
- `wav_url` - HTTP/HTTPS URL
- `wav_base64` - Base64 encoded string

**Audio Input (secondary, for multi-person):**
- `wav_path_2` - Local file path
- `wav_url_2` - HTTP/HTTPS URL
- `wav_base64_2` - Base64 encoded string

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | "A person talking naturally" | Text description |
| `width` | integer | 512 | Output width in pixels |
| `height` | integer | 512 | Output height in pixels |
| `max_frame` | integer | Auto-calculated | Maximum frames (based on audio duration) |
| `use_r2_storage` | boolean | false | Upload to R2 and return public URL |
| `network_volume` | boolean | false | Save to network volume and return path |

---

## Response Examples

### Success Response (R2 Storage)

```json
{
  "status": "success",
  "r2_url": "https://your-bucket.r2.dev/infinitetalk/output/1234567890_video.mp4",
  "file_size": 5242880,
  "filename": "1234567890_video.mp4"
}
```

### Success Response (Network Volume)

```json
{
  "status": "success",
  "video_path": "/runpod-volume/infinitetalk_task_abc123.mp4"
}
```

### Success Response (Base64)

```json
{
  "status": "success",
  "video": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ..."
}
```

### Error Response

```json
{
  "error": "Failed to process video: Invalid audio format"
}
```

---

## Postman Collection Setup

### 1. Create Environment Variables

In Postman, create a new environment with:

```
RUNPOD_ENDPOINT_ID = your-endpoint-id
RUNPOD_API_KEY = your-api-key
```

### 2. Import as Collection

1. Create a new Collection in Postman
2. Add requests using the examples above
3. Use variables: `{{RUNPOD_ENDPOINT_ID}}` and `{{RUNPOD_API_KEY}}`
4. Set request URL: `https://api.runpod.ai/v2/{{RUNPOD_ENDPOINT_ID}}/runsync`
5. Add Authorization header: `Bearer {{RUNPOD_API_KEY}}`

### 3. Pre-request Script (for Base64 conversion)

To convert local files to Base64 in Postman:

```javascript
// Read image file and convert to Base64
const fs = require('fs');
const imageData = fs.readFileSync('/path/to/image.jpg');
const base64Image = imageData.toString('base64');
pm.environment.set("image_base64", `data:image/jpeg;base64,${base64Image}`);

// Read audio file and convert to Base64
const audioData = fs.readFileSync('/path/to/audio.wav');
const base64Audio = audioData.toString('base64');
pm.environment.set("audio_base64", `data:audio/wav;base64,${base64Audio}`);
```

Then use `{{image_base64}}` and `{{audio_base64}}` in your request body.

---

## Testing Tips

1. **Start with sync endpoint** (`/runsync`) for quick tests
2. **Use async endpoint** (`/run`) for production/long videos
3. **Enable R2 storage** for easier result access via public URLs
4. **Test with example files** from the repository first
5. **Monitor logs** in RunPod dashboard for debugging
6. **Check file sizes** - keep under 100MB for faster processing
7. **Audio duration** determines video length automatically

---

## Common Issues

### 1. Timeout on Sync Endpoint
**Solution**: Use async endpoint (`/run`) instead of `/runsync`

### 2. Base64 Decode Error
**Solution**: Ensure Base64 string includes proper data URI prefix or is pure Base64

### 3. File Not Found
**Solution**: Check file paths are absolute and files exist in network volume

### 4. R2 Upload Failed
**Solution**: Verify R2 environment variables are set correctly

### 5. Out of Memory
**Solution**: Reduce `width`, `height`, or `max_frame` parameters

---

## Example Python Client

```python
import requests
import base64
import time

# Configuration
ENDPOINT_ID = "your-endpoint-id"
API_KEY = "your-api-key"
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Read and encode files
with open("image.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

with open("audio.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# Submit job
payload = {
    "input": {
        "input_type": "image",
        "person_count": "single",
        "image_base64": f"data:image/jpeg;base64,{image_b64}",
        "wav_base64": f"data:audio/wav;base64,{audio_b64}",
        "use_r2_storage": True
    }
}

# Use async endpoint
response = requests.post(f"{BASE_URL}/run", json=payload, headers=headers)
job_id = response.json()["id"]
print(f"Job ID: {job_id}")

# Poll for completion
while True:
    status_response = requests.get(f"{BASE_URL}/status/{job_id}", headers=headers)
    status_data = status_response.json()
    
    if status_data["status"] == "COMPLETED":
        result = status_data["output"]
        print(f"Video URL: {result['r2_url']}")
        break
    elif status_data["status"] == "FAILED":
        print(f"Error: {status_data.get('error')}")
        break
    
    print(f"Status: {status_data['status']}")
    time.sleep(5)
```

---

## Next Steps

1. Deploy your Docker image to RunPod Serverless
2. Configure R2 environment variables in RunPod dashboard
3. Test with the provided cURL examples
4. Import into Postman for easier testing
5. Integrate into your application using the Python client

For more details, see:
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment instructions
- [README.md](README.md) - Project overview
- [examples/client_example.py](examples/client_example.py) - Complete Python client
