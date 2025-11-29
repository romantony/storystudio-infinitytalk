"""
ComfyUI WebSocket Client
Handles communication with ComfyUI server via WebSocket
"""

import json
import urllib.request
import urllib.parse
import websocket
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ComfyUIClient:
    """Client for communicating with ComfyUI server"""
    
    def __init__(self, server_address: str = "127.0.0.1", port: int = 8188):
        """
        Initialize ComfyUI client
        
        Args:
            server_address: ComfyUI server address
            port: ComfyUI server port
        """
        self.server_address = server_address
        self.port = port
        self.base_url = f"http://{server_address}:{port}"
        self.ws_url = f"ws://{server_address}:{port}/ws"
        
        logger.info(f"ComfyUI Client initialized: {self.base_url}")
    
    def load_workflow(self, workflow_path: str) -> dict:
        """
        Load a workflow JSON file
        
        Args:
            workflow_path: Path to the workflow JSON file
            
        Returns:
            Workflow dictionary
        """
        with open(workflow_path, "r") as f:
            workflow = json.load(f)
        
        logger.info(f"Loaded workflow: {workflow_path} ({len(workflow)} nodes)")
        return workflow
    
    def queue_prompt(self, prompt: dict, client_id: str) -> Optional[str]:
        """
        Queue a prompt to ComfyUI
        
        Args:
            prompt: Workflow prompt dictionary
            client_id: Unique client ID
            
        Returns:
            Prompt ID if successful, None otherwise
        """
        url = f"{self.base_url}/prompt"
        
        data = json.dumps({
            "prompt": prompt,
            "client_id": client_id
        }).encode("utf-8")
        
        try:
            req = urllib.request.Request(url, data=data)
            req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read())
                prompt_id = result.get("prompt_id")
                
                logger.info(f"✅ Prompt queued: {prompt_id}")
                return prompt_id
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            logger.error(f"❌ HTTP error: {e.code} - {e.reason}")
            logger.error(f"Response: {error_body}")
            # Try to parse error details
            try:
                error_data = json.loads(error_body)
                if "error" in error_data:
                    logger.error(f"Error details: {json.dumps(error_data['error'], indent=2)}")
            except:
                pass
            return None
        except Exception as e:
            logger.error(f"❌ Failed to queue prompt: {e}")
            return None
    
    def get_history(self, prompt_id: str) -> Optional[dict]:
        """
        Get execution history for a prompt
        
        Args:
            prompt_id: Prompt ID to query
            
        Returns:
            History dictionary or None if not found
        """
        url = f"{self.base_url}/history/{prompt_id}"
        
        try:
            with urllib.request.urlopen(url) as response:
                history = json.loads(response.read())
                return history.get(prompt_id)
        except Exception as e:
            logger.error(f"❌ Failed to get history: {e}")
            return None
    
    def wait_for_completion(
        self,
        ws: websocket.WebSocket,
        prompt_id: str,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """
        Wait for prompt execution to complete via WebSocket
        
        Args:
            ws: WebSocket connection
            prompt_id: Prompt ID to wait for
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if completed successfully, False otherwise
        """
        logger.info(f"Waiting for completion: {prompt_id}")
        
        try:
            while True:
                out = ws.recv()
                
                if isinstance(out, str):
                    message = json.loads(out)
                    
                    if message["type"] == "executing":
                        data = message["data"]
                        
                        if data["node"] is not None:
                            logger.debug(f"Executing node: {data['node']}")
                            if progress_callback:
                                progress_callback(data)
                        
                        if data["node"] is None and data["prompt_id"] == prompt_id:
                            logger.info("✅ Execution completed")
                            return True
                    
                    elif message["type"] == "progress":
                        if progress_callback:
                            progress_callback(message["data"])
                    
                    elif message["type"] == "error":
                        logger.error(f"❌ Execution error: {message}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Error waiting for completion: {e}")
            return False
    
    def get_output_files(self, prompt_id: str) -> Dict[str, list]:
        """
        Get output files from execution history
        
        Args:
            prompt_id: Prompt ID to query
            
        Returns:
            Dictionary mapping node IDs to lists of output file paths
        """
        history = self.get_history(prompt_id)
        
        if not history:
            logger.error("No history found")
            return {}
        
        # Debug: Log the history structure
        import json
        logger.info(f"History structure: {json.dumps(history, indent=2, default=str)[:2000]}")
        
        # Check for errors in history
        if "status" in history:
            logger.info(f"Execution status: {history['status']}")
        if "messages" in history:
            logger.info(f"Execution messages: {history['messages']}")
        
        output_files = {}
        
        for node_id in history.get("outputs", {}):
            node_output = history["outputs"][node_id]
            files = []
            
            # Check for different output types (gifs, images, videos)
            # VHS nodes and other video nodes typically output to "videos"
            for output_type in ["gifs", "images", "videos"]:
                if output_type in node_output:
                    logger.info(f"Node {node_id} has {output_type}: {len(node_output[output_type])} item(s)")
                    for item in node_output[output_type]:
                        # Check for fullpath first (some nodes)
                        if "fullpath" in item:
                            files.append(item["fullpath"])
                        # Otherwise construct path from filename and subfolder
                        elif "filename" in item:
                            filename = item["filename"]
                            subfolder = item.get("subfolder", "")
                            item_type = item.get("type", output_type)
                            
                            # Construct the full path based on type
                            if item_type == "output" or item_type == output_type:
                                base_path = "/ComfyUI/output"
                            elif item_type == "input":
                                base_path = "/ComfyUI/input"
                            else:
                                base_path = "/ComfyUI/output"
                            
                            if subfolder:
                                full_path = f"{base_path}/{subfolder}/{filename}"
                            else:
                                full_path = f"{base_path}/{filename}"
                            
                            files.append(full_path)
                            logger.info(f"Constructed path: {full_path}")
            
            if files:
                output_files[node_id] = files
                logger.info(f"Node {node_id}: {len(files)} output file(s) found")
        
        return output_files
    
    def check_server_ready(self, timeout: int = 120) -> bool:
        """
        Check if ComfyUI server is ready
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if server is ready, False otherwise
        """
        import time
        
        logger.info("Checking if ComfyUI server is ready...")
        
        for attempt in range(timeout):
            try:
                urllib.request.urlopen(self.base_url, timeout=5)
                logger.info(f"✅ ComfyUI server is ready (attempt {attempt + 1})")
                return True
            except Exception:
                if attempt % 10 == 0:
                    logger.info(f"Waiting for ComfyUI... ({attempt}/{timeout})")
                time.sleep(1)
        
        logger.error("❌ ComfyUI server failed to start")
        return False
    
    def connect_websocket(self, client_id: str, timeout: int = 30) -> Optional[websocket.WebSocket]:
        """
        Connect to ComfyUI WebSocket
        
        Args:
            client_id: Unique client ID
            timeout: Connection timeout in seconds
            
        Returns:
            WebSocket connection or None if failed
        """
        import time
        
        ws_url = f"{self.ws_url}?clientId={client_id}"
        logger.info(f"Connecting to WebSocket: {ws_url}")
        
        for attempt in range(timeout):
            try:
                ws = websocket.WebSocket()
                ws.connect(ws_url)
                logger.info(f"✅ WebSocket connected (attempt {attempt + 1})")
                return ws
            except Exception as e:
                if attempt % 5 == 0:
                    logger.warning(f"WebSocket connection failed (attempt {attempt + 1}/{timeout}): {e}")
                time.sleep(1)
        
        logger.error("❌ Failed to connect to WebSocket")
        return None


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    client = ComfyUIClient()
    
    # Check if server is ready
    if client.check_server_ready(timeout=10):
        print("ComfyUI server is ready!")
    else:
        print("ComfyUI server is not responding")
