# InfiniteTalk Model

AI-powered lip-sync video generation from images/videos and audio using the InfiniteTalk model.

## 🎯 Features

- **Image-to-Video (I2V)**: Generate talking videos from static images
- **Video-to-Video (V2V)**: Add lip-sync to existing videos
- **Single & Multi-Person**: Support for both single and multi-person scenarios
- **High-Quality Lip-Sync**: Precise synchronization with audio
- **Flexible Input**: Support for URLs, local paths, and Base64 encoding
- **R2 Storage Integration**: Automatic upload to Cloudflare R2

## 📋 Workflow Types

The model automatically selects the appropriate workflow based on input parameters:

| input_type | person_count | Workflow | Description |
|------------|--------------|----------|-------------|
| `image` | `single` | I2V_single.json | Single person image to video |
| `image` | `multi` | I2V_multi.json | Multiple people image to video |
| `video` | `single` | V2V_single.json | Single person video to video |
| `video` | `multi` | V2V_multi.json | Multiple people video to video |

## 🚀 Deployment

### Build Docker Image

```bash
cd models/infinitetalk
docker build -t your-username/infinitetalk:latest .
docker push your-username/infinitetalk:latest
```

### Deploy to RunPod

1. Create a new Serverless Endpoint
2. Use the Docker image: `your-username/infinitetalk:latest`
3. Set environment variables for R2 storage (optional):
   - `R2_ACCOUNT_ID`
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`
   - `R2_PUBLIC_URL`

## 📝 API Reference

### Input Parameters

#### Workflow Selection
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_type` | string | No | `"image"` | Input type: `"image"` or `"video"` |
| `person_count` | string | No | `"single"` | Number of people: `"single"` or `"multi"` |

#### Media Input (choose one method)
**For Images (I2V):**
- `image_url`: URL to image file
- `image_path`: Local path to image file
- `image_base64`: Base64 encoded image

**For Videos (V2V):**
- `video_url`: URL to video file
- `video_path`: Local path to video file
- `video_base64`: Base64 encoded video

#### Audio Input (choose one method)
- `wav_url`: URL to audio file (WAV/MP3)
- `wav_path`: Local path to audio file
- `wav_base64`: Base64 encoded audio

**For Multi-Person (second audio):**
- `wav_url_2`: URL to second audio file
- `wav_path_2`: Local path to second audio
- `wav_base64_2`: Base64 encoded second audio

#### Other Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | No | `"A person talking naturally"` | Description for generation |
| `width` | integer | No | `512` | Output width in pixels |
| `height` | integer | No | `512` | Output height in pixels |
| `max_frame` | integer | No | Auto-calculated | Maximum frames (calculated from audio if not provided) |
| `use_r2_storage` | boolean | No | `false` | Upload to R2 and return URL |
| `network_volume` | boolean | No | `false` | Save to network volume |

### Request Examples

#### 1. I2V Single (Image-to-Video, Single Person)

```json
{
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
}
```

#### 2. I2V Multi (Image-to-Video, Multiple People)

```json
{
  "input": {
    "input_type": "image",
    "person_count": "multi",
    "prompt": "Two people having a conversation",
    "image_url": "https://example.com/portrait.jpg",
    "wav_url": "https://example.com/audio1.wav",
    "wav_url_2": "https://example.com/audio2.wav",
    "width": 512,
    "height": 512
  }
}
```

#### 3. V2V Single (Video-to-Video, Single Person)

```json
{
  "input": {
    "input_type": "video",
    "person_count": "single",
    "prompt": "A person singing",
    "video_url": "https://example.com/video.mp4",
    "wav_url": "https://example.com/audio.wav",
    "width": 512,
    "height": 512
  }
}
```

#### 4. Using Base64 Input

```json
{
  "input": {
    "input_type": "image",
    "person_count": "single",
    "prompt": "A person talking",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
    "wav_base64": "data:audio/wav;base64,UklGRiQA...",
    "width": 512,
    "height": 512
  }
}
```

### Response Formats

#### With R2 Storage
```json
{
  "status": "success",
  "r2_url": "https://your-bucket.r2.dev/infinitetalk/output/12345_video.mp4",
  "file_size": 1048576,
  "filename": "12345_video.mp4"
}
```

#### With Network Volume
```json
{
  "status": "success",
  "video_path": "/runpod-volume/infinitetalk_task_abc123.mp4"
}
```

#### Base64 Output (default)
```json
{
  "status": "success",
  "video": "data:video/mp4;base64,AAAAIGZ0eXBpc29t..."
}
```

#### Error Response
```json
{
  "error": "Failed to process video: invalid audio format"
}
```

## 🧪 Testing Locally

```bash
# Run the container locally
docker run -p 8188:8188 \
  -e R2_ACCOUNT_ID=your_id \
  -e R2_ACCESS_KEY_ID=your_key \
  -e R2_SECRET_ACCESS_KEY=your_secret \
  -e R2_BUCKET_NAME=your_bucket \
  infinitetalk:latest
```

Then test with:

```python
import requests

response = requests.post("http://localhost:8000/runsync", json={
    "input": {
        "input_type": "image",
        "person_count": "single",
        "image_url": "https://example.com/portrait.jpg",
        "wav_url": "https://example.com/audio.wav"
    }
})

print(response.json())
```

## 📚 Model Information

- **Base Model**: InfiniteTalk (Wan2.1)
- **Model Size**: 14B parameters
- **Quantization**: Q8 (8-bit quantization)
- **Input Resolution**: 480p (scalable)
- **Supported Audio**: WAV, MP3

## 🔧 Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce `width`, `height`, or `max_frame`
2. **Slow Generation**: This is normal for high-quality video generation
3. **Audio Sync Issues**: Ensure audio is clear and properly formatted

### Logs

Check logs for detailed error messages:
```bash
docker logs <container_id>
```

## 📄 License

This model implementation follows the Apache 2.0 License. The InfiniteTalk model has its own license terms.

## 🙏 Credits

- [InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk) - Original model
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - Workflow framework
- [RunPod](https://runpod.io/) - Serverless infrastructure
