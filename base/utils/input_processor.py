"""
Input Processor Utility
Handles different input types: URL, local path, and Base64
"""

import os
import base64
import urllib.request
import logging
from typing import Optional, Tuple
import binascii

logger = logging.getLogger(__name__)


def truncate_base64_for_log(base64_str: str, max_length: int = 50) -> str:
    """Truncate Base64 string for logging purposes"""
    if not base64_str:
        return ""
    return base64_str[:max_length] + "..." if len(base64_str) > max_length else base64_str


def download_file_from_url(url: str, output_path: str) -> str:
    """
    Download a file from URL
    
    Args:
        url: URL to download from
        output_path: Local path to save the file
        
    Returns:
        Path to the downloaded file
        
    Raises:
        Exception: If download fails
    """
    logger.info(f"Downloading from URL: {url}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download file
        urllib.request.urlretrieve(url, output_path)
        
        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Downloaded: {output_path} ({file_size} bytes)")
        
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Failed to download from {url}: {e}")
        raise


def save_base64_to_file(base64_data: str, output_path: str) -> str:
    """
    Decode and save Base64 data to a file
    
    Args:
        base64_data: Base64 encoded string (with or without data URI prefix)
        output_path: Local path to save the file
        
    Returns:
        Path to the saved file
        
    Raises:
        Exception: If decoding or saving fails
    """
    logger.info(f"Processing Base64 data: {truncate_base64_for_log(base64_data)}")
    
    try:
        # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
        if "," in base64_data and base64_data.startswith("data:"):
            base64_data = base64_data.split(",", 1)[1]
        
        # Decode Base64
        file_bytes = base64.b64decode(base64_data)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write to file
        with open(output_path, "wb") as f:
            f.write(file_bytes)
        
        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Saved Base64 data to: {output_path} ({file_size} bytes)")
        
        return output_path
        
    except binascii.Error as e:
        logger.error(f"❌ Base64 decoding error: {e}")
        raise ValueError(f"Invalid Base64 data: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to save Base64 data: {e}")
        raise


def process_input(
    input_data: str,
    temp_dir: str,
    output_filename: str,
    input_type: str
) -> str:
    """
    Process input data based on its type (path, URL, or Base64)
    
    Args:
        input_data: The input data (path, URL, or Base64 string)
        temp_dir: Temporary directory for downloads/conversions
        output_filename: Filename to use when saving
        input_type: Type of input - "path", "url", or "base64"
        
    Returns:
        Absolute path to the processed file
        
    Raises:
        Exception: If processing fails
    """
    os.makedirs(temp_dir, exist_ok=True)
    output_path = os.path.abspath(os.path.join(temp_dir, output_filename))
    
    if input_type == "path":
        # Local path - just return it (verify it exists)
        logger.info(f"📁 Using local path: {input_data}")
        if not os.path.exists(input_data):
            raise FileNotFoundError(f"File not found: {input_data}")
        return os.path.abspath(input_data)
        
    elif input_type == "url":
        # URL - download it
        logger.info(f"🌐 Processing URL input: {input_data}")
        return download_file_from_url(input_data, output_path)
        
    elif input_type == "base64":
        # Base64 - decode and save
        logger.info(f"🔢 Processing Base64 input")
        return save_base64_to_file(input_data, output_path)
        
    else:
        raise ValueError(f"Unsupported input type: {input_type}")


def detect_input_type(
    path_value: Optional[str],
    url_value: Optional[str],
    base64_value: Optional[str]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect which input type is provided and return the data and type
    
    Args:
        path_value: Value from *_path parameter
        url_value: Value from *_url parameter
        base64_value: Value from *_base64 parameter
        
    Returns:
        Tuple of (input_data, input_type) or (None, None) if none provided
    """
    if path_value:
        return path_value, "path"
    elif url_value:
        return url_value, "url"
    elif base64_value:
        return base64_value, "base64"
    else:
        return None, None


def process_media_input(
    job_input: dict,
    media_type: str,
    temp_dir: str,
    default_filename: str,
    default_path: Optional[str] = None
) -> str:
    """
    Process media input (image/video/audio) from job input
    
    Args:
        job_input: Job input dictionary
        media_type: Type of media - "image", "video", or "audio"
        temp_dir: Temporary directory
        default_filename: Default filename if input needs to be saved
        default_path: Default path to use if no input provided
        
    Returns:
        Path to the media file
        
    Raises:
        ValueError: If no valid input is provided and no default
    """
    # Determine parameter names based on media type
    if media_type == "audio":
        path_key, url_key, base64_key = "wav_path", "wav_url", "wav_base64"
    else:
        path_key = f"{media_type}_path"
        url_key = f"{media_type}_url"
        base64_key = f"{media_type}_base64"
    
    # Get input data
    input_data, input_type = detect_input_type(
        job_input.get(path_key),
        job_input.get(url_key),
        job_input.get(base64_key)
    )
    
    # Process input or use default
    if input_data and input_type:
        return process_input(input_data, temp_dir, default_filename, input_type)
    elif default_path:
        logger.info(f"No {media_type} input provided, using default: {default_path}")
        return default_path
    else:
        raise ValueError(f"No {media_type} input provided and no default available")


def encode_file_to_base64(file_path: str) -> str:
    """
    Encode a file to Base64 string
    
    Args:
        file_path: Path to the file to encode
        
    Returns:
        Base64 encoded string
    """
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_file_info(file_path: str) -> dict:
    """
    Get information about a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(file_path):
        return {"exists": False}
    
    return {
        "exists": True,
        "path": os.path.abspath(file_path),
        "size": os.path.getsize(file_path),
        "name": os.path.basename(file_path),
        "extension": os.path.splitext(file_path)[1]
    }


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Test URL download
    test_url = "https://example.com/image.jpg"
    # process_input(test_url, "/tmp/test", "downloaded.jpg", "url")
    
    # Test Base64
    test_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    # process_input(test_base64, "/tmp/test", "decoded.png", "base64")
    
    print("Input processor utility ready")
