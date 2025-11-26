"""
Cloudflare R2 Storage Utility
Handles file uploads to R2 and returns public URLs
"""

import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
from typing import Optional, Dict
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)


class R2Storage:
    """Cloudflare R2 Storage Client"""
    
    def __init__(
        self,
        account_id: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        public_url: Optional[str] = None
    ):
        """
        Initialize R2 Storage client
        
        Args:
            account_id: Cloudflare account ID
            access_key_id: R2 access key ID
            secret_access_key: R2 secret access key
            bucket_name: R2 bucket name
            public_url: Public URL for the bucket (e.g., https://your-bucket.r2.dev)
        """
        self.account_id = account_id or os.getenv("R2_ACCOUNT_ID")
        self.access_key_id = access_key_id or os.getenv("R2_ACCESS_KEY_ID")
        self.secret_access_key = secret_access_key or os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = bucket_name or os.getenv("R2_BUCKET_NAME")
        self.public_url = public_url or os.getenv("R2_PUBLIC_URL")
        
        if not all([self.account_id, self.access_key_id, self.secret_access_key, self.bucket_name]):
            raise ValueError("R2 credentials not properly configured. Set environment variables or pass them explicitly.")
        
        # Initialize S3 client for R2
        self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto"
        )
        
        logger.info(f"R2 Storage initialized with bucket: {self.bucket_name}")
    
    def upload_file(
        self,
        file_path: str,
        object_key: Optional[str] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Upload a file to R2 storage
        
        Args:
            file_path: Local path to the file to upload
            object_key: Key (path) in the bucket. If None, uses filename
            content_type: MIME type of the file. Auto-detected if None
            metadata: Additional metadata to store with the file
            
        Returns:
            Public URL of the uploaded file, or None if upload failed
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        # Generate object key if not provided
        if object_key is None:
            filename = os.path.basename(file_path)
            object_key = f"runpod/output/{filename}"
        
        # Auto-detect content type
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = "application/octet-stream"
        
        try:
            # Prepare upload arguments
            upload_args = {
                "Bucket": self.bucket_name,
                "Key": object_key,
                "ContentType": content_type
            }
            
            if metadata:
                upload_args["Metadata"] = metadata
            
            # Upload file
            logger.info(f"Uploading {file_path} to R2: {object_key}")
            with open(file_path, "rb") as f:
                self.client.put_object(
                    Body=f,
                    **upload_args
                )
            
            # Generate public URL
            if self.public_url:
                public_url = f"{self.public_url.rstrip('/')}/{object_key}"
            else:
                # Fallback to direct R2 URL (may not be public)
                public_url = f"{self.endpoint_url}/{self.bucket_name}/{object_key}"
            
            file_size = os.path.getsize(file_path)
            logger.info(f"✅ Upload successful: {public_url} ({file_size} bytes)")
            
            return public_url
            
        except ClientError as e:
            logger.error(f"❌ Failed to upload to R2: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during upload: {e}")
            return None
    
    def upload_file_with_metadata(
        self,
        file_path: str,
        prefix: str = "output",
        extra_metadata: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, str]]:
        """
        Upload file with automatic metadata generation
        
        Args:
            file_path: Local path to the file
            prefix: Prefix for the object key (folder in bucket)
            extra_metadata: Additional metadata to include
            
        Returns:
            Dict with url, size, and other metadata, or None if failed
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        # Generate unique object key with timestamp
        import time
        filename = os.path.basename(file_path)
        timestamp = int(time.time())
        object_key = f"{prefix}/{timestamp}_{filename}"
        
        # Prepare metadata
        file_size = os.path.getsize(file_path)
        metadata = {
            "original-filename": filename,
            "upload-timestamp": str(timestamp),
            "file-size": str(file_size)
        }
        
        if extra_metadata:
            metadata.update(extra_metadata)
        
        # Upload
        url = self.upload_file(file_path, object_key, metadata=metadata)
        
        if url:
            return {
                "url": url,
                "object_key": object_key,
                "size": file_size,
                "timestamp": timestamp,
                "filename": filename
            }
        
        return None
    
    def delete_file(self, object_key: str) -> bool:
        """
        Delete a file from R2 storage
        
        Args:
            object_key: Key of the object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            logger.info(f"Deleted from R2: {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete from R2: {e}")
            return False
    
    def file_exists(self, object_key: str) -> bool:
        """
        Check if a file exists in R2 storage
        
        Args:
            object_key: Key of the object to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            return True
        except ClientError:
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 100) -> list:
        """
        List files in R2 storage
        
        Args:
            prefix: Filter by prefix (folder path)
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object keys
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if "Contents" in response:
                return [obj["Key"] for obj in response["Contents"]]
            return []
            
        except ClientError as e:
            logger.error(f"Failed to list files from R2: {e}")
            return []


def upload_to_r2(
    file_path: str,
    prefix: str = "output",
    **kwargs
) -> Optional[str]:
    """
    Convenience function to upload a file to R2
    
    Args:
        file_path: Path to the file to upload
        prefix: Prefix for the object key
        **kwargs: Additional arguments for R2Storage
        
    Returns:
        Public URL of the uploaded file, or None if failed
    """
    try:
        r2 = R2Storage(**kwargs)
        result = r2.upload_file_with_metadata(file_path, prefix=prefix)
        return result["url"] if result else None
    except Exception as e:
        logger.error(f"Failed to upload to R2: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize R2 client (credentials from environment variables)
    r2 = R2Storage()
    
    # Upload a file
    test_file = "test_video.mp4"
    if os.path.exists(test_file):
        result = r2.upload_file_with_metadata(
            test_file,
            prefix="test",
            extra_metadata={"model": "infinitetalk", "version": "1.0"}
        )
        
        if result:
            print(f"✅ Upload successful!")
            print(f"URL: {result['url']}")
            print(f"Size: {result['size']} bytes")
        else:
            print("❌ Upload failed")
