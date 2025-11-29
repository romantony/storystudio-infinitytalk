"""
Local test script for InfiniteTalk handler
Tests the handler without RunPod infrastructure
"""

import json
import sys
import time

# Simulate a RunPod job
def create_test_job():
    """Create a test job with sample inputs"""
    return {
        "input": {
            "input_type": "image",
            "person_count": "single",
            "prompt": "A person giving a motivational speech",
            # Use the provided test URLs
            "image_url": "https://parentearn.com/test_user_123/test-project/assets/b56a0b37b41fcfc852219deff273c833_1764148926.png",
            "audio_url": "https://parentearn.com/test_user_123/test-project/assets/30sec-Motivation_speech.mp3",
            "width": 512,
            "height": 512,
            "max_frame": 150,  # ~5 seconds at 30fps
            "use_r2_storage": True,  # Upload to R2 storage
            "network_volume": False
        }
    }


def test_handler():
    """Test the handler with a sample job"""
    print("=" * 60)
    print("Testing InfiniteTalk Handler Locally")
    print("=" * 60)
    
    # Import the handler
    sys.path.append('/base')
    from handler import InfiniteTalkHandler
    
    # Create handler instance
    handler = InfiniteTalkHandler()
    print(f"✅ Handler initialized: {handler.model_name}")
    print(f"✅ ComfyUI client ready")
    print(f"✅ R2 Storage: {'Enabled' if handler.r2_enabled else 'Disabled'}")
    print()
    
    # Create test job
    job = create_test_job()
    print("Test Job Input:")
    print(json.dumps(job, indent=2))
    print()
    
    # Run the handler
    print("Running handler...")
    start_time = time.time()
    
    try:
        result = handler.handler(job)
        elapsed = time.time() - start_time
        
        print()
        print("=" * 60)
        print(f"Handler completed in {elapsed:.2f} seconds")
        print("=" * 60)
        print()
        
        # Print result (truncate base64 if present)
        if "video" in result and isinstance(result["video"], str):
            result_display = result.copy()
            video_data = result_display["video"]
            if len(video_data) > 100:
                result_display["video"] = f"{video_data[:50]}... [{len(video_data)} chars total]"
            print("Result:")
            print(json.dumps(result_display, indent=2))
        else:
            print("Result:")
            print(json.dumps(result, indent=2))
        
        # Check for success
        if result.get("status") == "success":
            print()
            print("✅ TEST PASSED!")
            if "video" in result:
                print(f"   Video data length: {len(result['video'])} chars")
            elif "video_path" in result:
                print(f"   Video path: {result['video_path']}")
            elif "r2_url" in result:
                print(f"   R2 URL: {result['r2_url']}")
            return 0
        else:
            print()
            print("❌ TEST FAILED!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        elapsed = time.time() - start_time
        print()
        print("=" * 60)
        print(f"Handler failed after {elapsed:.2f} seconds")
        print("=" * 60)
        print()
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = test_handler()
    sys.exit(exit_code)
