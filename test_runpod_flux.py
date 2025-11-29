"""
Test script for RunPod ComfyUI with FLUX model
"""
import requests
import json
import time
import websocket
import uuid

COMFYUI_URL = "http://localhost:8188"

# Simple FLUX workflow
workflow = {
    "3": {
        "inputs": {
            "seed": 42,
            "steps": 20,
            "cfg": 3.5,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1,
            "model": ["10", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
    },
    "5": {
        "inputs": {
            "width": 512,
            "height": 512,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
    },
    "6": {
        "inputs": {
            "text": "a beautiful landscape with mountains and a lake at sunset, highly detailed, photorealistic",
            "clip": ["10", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "7": {
        "inputs": {
            "text": "blurry, bad quality, low resolution",
            "clip": ["10", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "8": {
        "inputs": {
            "samples": ["3", 0],
            "vae": ["10", 2]
        },
        "class_type": "VAEDecode"
    },
    "9": {
        "inputs": {
            "filename_prefix": "flux_test",
            "images": ["8", 0]
        },
        "class_type": "SaveImage"
    },
    "10": {
        "inputs": {
            "ckpt_name": "flux1-dev-fp8.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
    }
}

def queue_prompt(workflow):
    """Queue a workflow for execution"""
    p = {"prompt": workflow}
    data = json.dumps(p).encode('utf-8')
    response = requests.post(f"{COMFYUI_URL}/prompt", data=data)
    return response.json()

def get_history(prompt_id):
    """Get execution history for a prompt"""
    response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
    return response.json()

def check_status():
    """Check if ComfyUI is responsive"""
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats")
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("Testing RunPod ComfyUI with FLUX model...")
    
    # Check if ComfyUI is running
    if not check_status():
        print("❌ ComfyUI is not accessible at", COMFYUI_URL)
        exit(1)
    
    print("✅ ComfyUI is accessible")
    
    # Queue the workflow
    print("\nQueuing FLUX workflow...")
    result = queue_prompt(workflow)
    
    if "prompt_id" in result:
        prompt_id = result["prompt_id"]
        print(f"✅ Workflow queued with ID: {prompt_id}")
        
        # Wait for execution
        print("\nWaiting for execution to complete...")
        for i in range(60):  # Wait up to 60 seconds
            time.sleep(1)
            history = get_history(prompt_id)
            
            if prompt_id in history:
                status = history[prompt_id].get("status", {})
                if status.get("completed", False):
                    print(f"\n✅ Execution completed!")
                    
                    # Check for outputs
                    outputs = history[prompt_id].get("outputs", {})
                    if outputs:
                        print(f"\n📁 Generated outputs:")
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                for img in node_output["images"]:
                                    print(f"  - {img.get('filename', 'unknown')}")
                    break
                elif "error" in status:
                    print(f"\n❌ Execution failed: {status.get('error')}")
                    break
            
            if i % 10 == 0 and i > 0:
                print(f"Still waiting... ({i}s)")
        else:
            print("\n⏱️ Timeout waiting for execution")
    else:
        print(f"❌ Failed to queue workflow: {result}")
