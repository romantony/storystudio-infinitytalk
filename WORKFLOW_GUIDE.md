# Workflow Configuration Guide

## Overview

This guide explains how to obtain, configure, and customize ComfyUI workflow files for the InfiniteTalk model and other models you may add.

## Obtaining Workflow Files

### Method 1: From Reference Repository

The original InfiniteTalk workflows are available at:
https://github.com/wlsdml1114/Infinitetalk_Runpod_hub

1. Navigate to the repository
2. Download these workflow JSON files:
   - `I2V_single.json` - Image-to-Video, single person
   - `I2V_multi.json` - Image-to-Video, multiple people
   - `V2V_single.json` - Video-to-Video, single person
   - `V2V_multi.json` - Video-to-Video, multiple people

3. Place them in: `models/infinitetalk/workflows/`

### Method 2: Export from ComfyUI

If you have a working ComfyUI setup with InfiniteTalk:

1. Start ComfyUI:
```bash
cd /path/to/ComfyUI
python main.py
```

2. Open browser to `http://localhost:8188`

3. Load the InfiniteTalk workflow

4. Configure all nodes as needed

5. Click **"Save (API Format)"** to export as JSON

6. Save with appropriate filename (e.g., `I2V_single.json`)

## Workflow Structure

Each workflow JSON file contains:

```json
{
  "node_id": {
    "inputs": {
      "parameter_name": "value",
      "input_connections": ["previous_node_id", output_index]
    },
    "class_type": "NodeClassName",
    "_meta": {
      "title": "Node Display Name"
    }
  }
}
```

## Key Node Types in InfiniteTalk

### 1. Load Image Node (ID: 284)
```json
"284": {
  "inputs": {
    "image": "/path/to/image.jpg"
  },
  "class_type": "LoadImage"
}
```

### 2. Load Video Node (ID: 228)
```json
"228": {
  "inputs": {
    "video": "/path/to/video.mp4",
    "force_rate": 0,
    "force_size": "Disabled",
    "frame_load_cap": 0,
    "skip_first_frames": 0
  },
  "class_type": "VHS_LoadVideo"
}
```

### 3. Load Audio Node (ID: 125)
```json
"125": {
  "inputs": {
    "audio": "/path/to/audio.wav"
  },
  "class_type": "VHS_LoadAudio"
}
```

### 4. Text Prompt Node (ID: 241)
```json
"241": {
  "inputs": {
    "positive_prompt": "A person talking naturally",
    "negative_prompt": "blurry, low quality"
  },
  "class_type": "CLIPTextEncode"
}
```

### 5. Dimension Nodes (IDs: 245, 246)
```json
"245": {
  "inputs": {
    "value": 512  // width
  },
  "class_type": "WAS_Number"
}
```

### 6. Max Frame Node (ID: 270)
```json
"270": {
  "inputs": {
    "value": 100  // max frames
  },
  "class_type": "WAS_Number"
}
```

### 7. Second Audio Node for Multi-Person
- I2V Multi: Node ID 307
- V2V Multi: Node ID 313

## Customizing Workflows

### 1. Change Model Weights

Find the model loader node and update the checkpoint path:

```json
"model_loader_node": {
  "inputs": {
    "ckpt_name": "Wan2_1-InfiniteTalk_Single_Q8.gguf"
  }
}
```

Available models:
- `Wan2_1-InfiniteTalk_Single_Q8.gguf` - Single person
- `Wan2_1-InfiniteTalk_Multi_Q8.gguf` - Multiple people
- `wan2.1-i2v-14b-480p-Q8_0.gguf` - General I2V

### 2. Add Custom Nodes

If you need additional processing:

1. Install custom node in Docker:
```dockerfile
RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/user/CustomNode && \
    cd CustomNode && \
    pip install -r requirements.txt
```

2. Add node to workflow JSON:
```json
"new_node_id": {
  "inputs": {
    "input": ["previous_node_id", 0],
    "parameter": "value"
  },
  "class_type": "CustomNodeClass"
}
```

3. Update connections in subsequent nodes

### 3. Modify Default Parameters

Common parameters to adjust:

```json
{
  "width": 512,           // Output width (256-1024)
  "height": 512,          // Output height (256-1024)
  "max_frame": 100,       // Maximum frames to generate
  "steps": 20,            // Diffusion steps (higher = better quality, slower)
  "cfg_scale": 7.5,       // Guidance scale (higher = more prompt adherence)
  "seed": -1,             // Random seed (-1 = random)
  "denoise": 1.0          // Denoising strength (0-1)
}
```

## Handler Integration

The handler modifies these nodes dynamically:

```python
def configure_workflow(self, workflow, job_input, processed_inputs):
    # Set media input (image or video)
    if self.is_i2v:
        workflow["284"]["inputs"]["image"] = processed_inputs['media']
    else:
        workflow["228"]["inputs"]["video"] = processed_inputs['media']
    
    # Set audio
    workflow["125"]["inputs"]["audio"] = processed_inputs['audio']
    
    # Set prompt
    workflow["241"]["inputs"]["positive_prompt"] = job_input.get('prompt')
    
    # Set dimensions
    workflow["245"]["inputs"]["value"] = job_input.get('width', 512)
    workflow["246"]["inputs"]["value"] = job_input.get('height', 512)
    
    # Set max frames
    workflow["270"]["inputs"]["value"] = self.calculate_max_frames(
        processed_inputs['audio']
    )
    
    # Multi-person: set second audio
    if self.is_multi:
        audio_node_id = "307" if self.is_i2v else "313"
        workflow[audio_node_id]["inputs"]["audio"] = processed_inputs['audio2']
```

## Workflow Validation

### Testing in ComfyUI

1. Load your workflow JSON in ComfyUI
2. Queue prompt and check for errors
3. Verify all nodes execute successfully
4. Check output quality and format

### Testing with Handler

```python
# Test workflow loading
from base.handler_base import BaseHandler

handler = YourModelHandler()
workflow = handler.load_workflow('/path/to/workflow.json')

# Validate required nodes exist
required_nodes = ["284", "125", "241", "245", "246", "270"]
for node_id in required_nodes:
    assert node_id in workflow, f"Missing node: {node_id}"
```

## Debugging Workflows

### Common Issues

1. **Missing Node Error**
   - Symptom: `Node type 'XYZ' not found`
   - Solution: Install required custom node

2. **Invalid Connection**
   - Symptom: Workflow fails to execute
   - Solution: Check node connections match output types

3. **File Not Found**
   - Symptom: Media files not loading
   - Solution: Verify file paths are absolute and accessible

### Logging

Enable detailed logging in handler:

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log workflow before execution
logger.debug(f"Workflow nodes: {list(workflow.keys())}")
logger.debug(f"Node 284 inputs: {workflow['284']['inputs']}")
```

## Performance Optimization

### Reduce Memory Usage

1. Lower max_frame value
2. Reduce output dimensions
3. Use quantized models (Q8, Q4)
4. Enable model offloading

### Speed Up Generation

1. Reduce diffusion steps (careful: quality impact)
2. Use smaller models when appropriate
3. Enable xformers attention optimization
4. Use TensorRT acceleration (if compatible)

## Creating New Workflows

### 1. Start from Template

Copy an existing workflow:
```bash
cp models/infinitetalk/workflows/I2V_single.json models/newmodel/workflows/base.json
```

### 2. Modify in ComfyUI

1. Load template in ComfyUI
2. Replace model loader nodes
3. Adjust parameters
4. Add/remove nodes as needed
5. Test thoroughly
6. Export as JSON

### 3. Update Handler

```python
class NewModelHandler(BaseHandler):
    def get_workflow_path(self, job_input):
        return "/workflows/base.json"
    
    def configure_workflow(self, workflow, job_input, processed_inputs):
        # Configure your specific nodes
        workflow["your_node"]["inputs"]["param"] = job_input.get('value')
```

## Best Practices

1. **Version Control**: Keep workflow files in git
2. **Documentation**: Comment complex node configurations
3. **Testing**: Test with various inputs before deployment
4. **Backup**: Keep working copies before modifications
5. **Validation**: Validate JSON syntax before use
6. **Node IDs**: Document important node IDs in comments
7. **Defaults**: Set sensible defaults for all parameters

## Resources

- **ComfyUI Documentation**: https://github.com/comfyanonymous/ComfyUI
- **ComfyUI Custom Nodes**: https://github.com/ltdrdata/ComfyUI-Manager
- **InfiniteTalk Reference**: https://github.com/wlsdml1114/Infinitetalk_Runpod_hub
- **Workflow Sharing**: https://comfyworkflows.com

## Support

If you encounter issues with workflows:

1. Validate JSON syntax: `python -m json.tool workflow.json`
2. Check ComfyUI logs for errors
3. Test workflow in ComfyUI UI first
4. Verify all custom nodes are installed
5. Check handler log output for node configuration
