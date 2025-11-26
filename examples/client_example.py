"""
Example Client Script for Testing RunPod Endpoints
"""

import requests
import os
import json
import time
from typing import Optional, Dict, Any


class RunPodClient:
    """Client for interacting with RunPod serverless endpoints"""
    
    def __init__(self, endpoint_id: str, api_key: str):
        """
        Initialize RunPod client
        
        Args:
            endpoint_id: Your RunPod endpoint ID
            api_key: Your RunPod API key
        """
        self.endpoint_id = endpoint_id
        self.api_key = api_key
        self.base_url = f"https://api.runpod.ai/v2/{endpoint_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def run_sync(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a synchronous request (waits for completion)
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Response dictionary
        """
        url = f"{self.base_url}/runsync"
        
        payload = {"input": input_data}
        
        print(f"Sending request to: {url}")
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")
    
    def run_async(self, input_data: Dict[str, Any]) -> str:
        """
        Run an asynchronous request (returns job ID)
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Job ID
        """
        url = f"{self.base_url}/run"
        
        payload = {"input": input_data}
        
        response = requests.post(url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("id")
        else:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")
    
    def check_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of an async job
        
        Args:
            job_id: Job ID to check
            
        Returns:
            Status dictionary
        """
        url = f"{self.base_url}/status/{job_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Status check failed: {response.status_code} - {response.text}")
    
    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: int = 5,
        max_wait: int = 600
    ) -> Dict[str, Any]:
        """
        Wait for an async job to complete
        
        Args:
            job_id: Job ID to wait for
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait
            
        Returns:
            Final result dictionary
        """
        elapsed = 0
        
        while elapsed < max_wait:
            status = self.check_status(job_id)
            job_status = status.get("status")
            
            print(f"Status: {job_status} (elapsed: {elapsed}s)")
            
            if job_status == "COMPLETED":
                return status
            elif job_status == "FAILED":
                raise Exception(f"Job failed: {status.get('error')}")
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        raise Exception(f"Job timed out after {max_wait} seconds")


def example_infinitetalk_i2v_single():
    """Example: InfiniteTalk Image-to-Video Single Person"""
    
    # Configuration
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID", "your-endpoint-id")
    api_key = os.getenv("RUNPOD_API_KEY", "your-api-key")
    
    client = RunPodClient(endpoint_id, api_key)
    
    # Input data
    input_data = {
        "input_type": "image",
        "person_count": "single",
        "prompt": "A person talking naturally",
        "image_url": "https://example.com/portrait.jpg",
        "wav_url": "https://example.com/audio.wav",
        "width": 512,
        "height": 512,
        "use_r2_storage": True
    }
    
    # Run synchronously
    print("Sending request...")
    result = client.run_sync(input_data)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    if result.get("status") == "success":
        if "r2_url" in result:
            print(f"\n✅ Video URL: {result['r2_url']}")
        elif "video_path" in result:
            print(f"\n✅ Video Path: {result['video_path']}")
        else:
            print(f"\n✅ Video generated (Base64)")
    else:
        print(f"\n❌ Error: {result.get('error')}")


def example_infinitetalk_i2v_multi():
    """Example: InfiniteTalk Image-to-Video Multiple People"""
    
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    api_key = os.getenv("RUNPOD_API_KEY")
    
    client = RunPodClient(endpoint_id, api_key)
    
    input_data = {
        "input_type": "image",
        "person_count": "multi",
        "prompt": "Two people having a conversation",
        "image_url": "https://example.com/portrait.jpg",
        "wav_url": "https://example.com/audio1.wav",
        "wav_url_2": "https://example.com/audio2.wav",
        "width": 512,
        "height": 512,
        "use_r2_storage": True
    }
    
    # Run asynchronously
    print("Submitting job...")
    job_id = client.run_async(input_data)
    print(f"Job ID: {job_id}")
    
    # Wait for completion
    print("Waiting for completion...")
    result = client.wait_for_completion(job_id)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    print("=== RunPod Client Examples ===\n")
    
    # Example 1: Single person I2V
    print("Example 1: Image-to-Video Single Person")
    example_infinitetalk_i2v_single()
    
    # Uncomment to run more examples:
    # print("\n" + "="*50 + "\n")
    # print("Example 2: Image-to-Video Multiple People")
    # example_infinitetalk_i2v_multi()
