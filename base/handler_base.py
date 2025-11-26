"""
Base Handler for RunPod Serverless Models
Provides common functionality for all model handlers
"""

import runpod
import os
import json
import uuid
import logging
import base64
import shutil
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Import utilities
import sys
sys.path.append('/base')
from utils.input_processor import process_media_input, truncate_base64_for_log
from utils.comfyui_client import ComfyUIClient
from utils.r2_storage import R2Storage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Base handler class for RunPod serverless models"""
    
    def __init__(
        self,
        model_name: str,
        server_address: str = "127.0.0.1",
        server_port: int = 8188
    ):
        """
        Initialize base handler
        
        Args:
            model_name: Name of the model
            server_address: ComfyUI server address
            server_port: ComfyUI server port
        """
        self.model_name = model_name
        self.comfy_client = ComfyUIClient(server_address, server_port)
        self.client_id = str(uuid.uuid4())
        
        # Check if R2 storage is configured
        self.r2_enabled = all([
            os.getenv("R2_ACCOUNT_ID"),
            os.getenv("R2_ACCESS_KEY_ID"),
            os.getenv("R2_SECRET_ACCESS_KEY"),
            os.getenv("R2_BUCKET_NAME")
        ])
        
        if self.r2_enabled:
            self.r2_client = R2Storage()
            logger.info("✅ R2 Storage enabled")
        else:
            self.r2_client = None
            logger.info("⚠️  R2 Storage not configured")
        
        logger.info(f"Handler initialized for model: {model_name}")
    
    @abstractmethod
    def get_workflow_path(self, job_input: dict) -> str:
        """
        Get the workflow file path based on input parameters
        
        Args:
            job_input: Job input dictionary
            
        Returns:
            Path to the workflow JSON file
        """
        pass
    
    @abstractmethod
    def configure_workflow(self, workflow: dict, job_input: dict, media_paths: dict) -> dict:
        """
        Configure the workflow with input parameters
        
        Args:
            workflow: Loaded workflow dictionary
            job_input: Job input dictionary
            media_paths: Dictionary of media file paths
            
        Returns:
            Configured workflow dictionary
        """
        pass
    
    def process_inputs(self, job_input: dict) -> Dict[str, str]:
        """
        Process all inputs (images, videos, audio)
        Override this method for model-specific input processing
        
        Args:
            job_input: Job input dictionary
            
        Returns:
            Dictionary of processed file paths
        """
        task_id = f"task_{uuid.uuid4()}"
        temp_dir = f"/tmp/{task_id}"
        os.makedirs(temp_dir, exist_ok=True)
        
        return {"temp_dir": temp_dir}
    
    def handle_output(
        self,
        output_files: Dict[str, list],
        job_input: dict,
        temp_dir: str
    ) -> dict:
        """
        Handle output files (upload to R2, encode to base64, or return path)
        
        Args:
            output_files: Dictionary of output files from ComfyUI
            job_input: Original job input
            temp_dir: Temporary directory path
            
        Returns:
            Response dictionary
        """
        # Find the first output file
        output_path = None
        for node_id, files in output_files.items():
            if files:
                output_path = files[0]
                logger.info(f"Found output file: {output_path}")
                break
        
        if not output_path or not os.path.exists(output_path):
            logger.error("No output file found")
            return {"error": "No output file generated"}
        
        # Check output handling preference
        use_r2 = job_input.get("use_r2_storage", False)
        use_network_volume = job_input.get("network_volume", False)
        
        if use_r2 and self.r2_enabled:
            # Upload to R2
            logger.info("Uploading to R2 storage...")
            result = self.r2_client.upload_file_with_metadata(
                output_path,
                prefix=f"{self.model_name}/output",
                extra_metadata={
                    "model": self.model_name,
                    "task_id": os.path.basename(temp_dir)
                }
            )
            
            if result:
                return {
                    "status": "success",
                    "r2_url": result["url"],
                    "file_size": result["size"],
                    "filename": result["filename"]
                }
            else:
                return {"error": "Failed to upload to R2"}
        
        elif use_network_volume:
            # Copy to network volume
            volume_path = os.getenv("NETWORK_VOLUME_PATH", "/runpod-volume")
            output_filename = f"{self.model_name}_{os.path.basename(temp_dir)}.mp4"
            dest_path = os.path.join(volume_path, output_filename)
            
            logger.info(f"Copying to network volume: {dest_path}")
            shutil.copy2(output_path, dest_path)
            
            return {
                "status": "success",
                "video_path": dest_path
            }
        
        else:
            # Return as Base64
            logger.info("Encoding output to Base64...")
            try:
                with open(output_path, "rb") as f:
                    video_data = base64.b64encode(f.read()).decode("utf-8")
                
                return {
                    "status": "success",
                    "video": video_data
                }
            except Exception as e:
                logger.error(f"Failed to encode output: {e}")
                return {"error": f"Failed to encode output: {e}"}
    
    def handler(self, job: dict) -> dict:
        """
        Main handler function called by RunPod
        
        Args:
            job: Job dictionary from RunPod
            
        Returns:
            Response dictionary
        """
        job_input = job.get("input", {})
        
        # Log input (truncate base64)
        log_input = job_input.copy()
        for key in list(log_input.keys()):
            if "base64" in key and log_input[key]:
                log_input[key] = truncate_base64_for_log(log_input[key])
        
        logger.info(f"Received job: {json.dumps(log_input, indent=2)}")
        
        temp_dir = None
        
        try:
            # Step 1: Process inputs
            logger.info("Step 1: Processing inputs...")
            media_paths = self.process_inputs(job_input)
            temp_dir = media_paths.get("temp_dir")
            
            # Step 2: Get workflow
            logger.info("Step 2: Loading workflow...")
            workflow_path = self.get_workflow_path(job_input)
            workflow = self.comfy_client.load_workflow(workflow_path)
            
            # Step 3: Configure workflow
            logger.info("Step 3: Configuring workflow...")
            workflow = self.configure_workflow(workflow, job_input, media_paths)
            
            # Step 4: Connect to ComfyUI
            logger.info("Step 4: Connecting to ComfyUI...")
            ws = self.comfy_client.connect_websocket(self.client_id)
            if not ws:
                return {"error": "Failed to connect to ComfyUI WebSocket"}
            
            # Step 5: Queue prompt
            logger.info("Step 5: Queueing prompt...")
            prompt_id = self.comfy_client.queue_prompt(workflow, self.client_id)
            if not prompt_id:
                ws.close()
                return {"error": "Failed to queue prompt"}
            
            # Step 6: Wait for completion
            logger.info("Step 6: Waiting for execution...")
            success = self.comfy_client.wait_for_completion(ws, prompt_id)
            ws.close()
            
            if not success:
                return {"error": "Execution failed"}
            
            # Step 7: Get output files
            logger.info("Step 7: Retrieving output files...")
            output_files = self.comfy_client.get_output_files(prompt_id)
            
            if not output_files:
                return {"error": "No output files generated"}
            
            # Step 8: Handle output
            logger.info("Step 8: Processing output...")
            result = self.handle_output(output_files, job_input, temp_dir)
            
            logger.info("✅ Job completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Job failed: {e}", exc_info=True)
            return {"error": str(e)}
        
        finally:
            # Cleanup temp directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {e}")


def start_handler(handler_instance: BaseHandler):
    """
    Start the RunPod serverless handler
    
    Args:
        handler_instance: Instance of a BaseHandler subclass
    """
    logger.info(f"Starting RunPod handler for {handler_instance.model_name}")
    runpod.serverless.start({"handler": handler_instance.handler})


if __name__ == "__main__":
    logger.info("Base handler module loaded")
