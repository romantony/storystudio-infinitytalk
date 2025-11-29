"""
InfiniteTalk Handler for RunPod Serverless
Handles lip-sync video generation from images/videos and audio
"""

import sys
sys.path.append('/base')

from handler_base import BaseHandler, start_handler
from utils.input_processor import process_media_input
import librosa
import logging

logger = logging.getLogger(__name__)


class InfiniteTalkHandler(BaseHandler):
    """Handler for InfiniteTalk model"""
    
    def __init__(self):
        super().__init__(model_name="infinitetalk")
    
    def get_workflow_path(self, job_input: dict) -> str:
        """
        Get workflow path based on input type and person count
        
        Workflow selection:
        - I2V_single.json: image + single person
        - I2V_multi.json: image + multiple people
        - V2V_single.json: video + single person
        - V2V_multi.json: video + multiple people
        """
        input_type = job_input.get("input_type", "image")  # "image" or "video"
        person_count = job_input.get("person_count", "single")  # "single" or "multi"
        
        if input_type == "image":
            if person_count == "single":
                workflow_path = "/workflows/I2V_single.json"
            else:
                workflow_path = "/workflows/I2V_multi.json"
        else:  # video
            if person_count == "single":
                workflow_path = "/workflows/V2V_single.json"
            else:
                workflow_path = "/workflows/V2V_multi.json"
        
        logger.info(f"Selected workflow: {workflow_path} (type={input_type}, count={person_count})")
        return workflow_path
    
    def process_inputs(self, job_input: dict) -> dict:
        """Process all input files"""
        # Get temp directory
        base_paths = super().process_inputs(job_input)
        temp_dir = base_paths["temp_dir"]
        
        input_type = job_input.get("input_type", "image")
        person_count = job_input.get("person_count", "single")
        
        # Process media (image or video)
        if input_type == "image":
            media_path = process_media_input(
                job_input,
                "image",
                temp_dir,
                "input_image.jpg",
                default_path="/examples/image.jpg"
            )
        else:
            media_path = process_media_input(
                job_input,
                "video",
                temp_dir,
                "input_video.mp4",
                default_path="/examples/video.mp4"
            )
        
        # Process primary audio
        wav_path = process_media_input(
            job_input,
            "audio",
            temp_dir,
            "input_audio.wav",
            default_path="/examples/audio.mp3"
        )
        
        # Process second audio for multi-person
        wav_path_2 = None
        if person_count == "multi":
            try:
                wav_path_2 = process_media_input(
                    job_input,
                    "audio",
                    temp_dir,
                    "input_audio_2.wav",
                    default_path=wav_path  # Use same audio if not provided
                )
            except:
                wav_path_2 = wav_path  # Fallback to primary audio
                logger.info("Using primary audio for second person")
        
        return {
            "temp_dir": temp_dir,
            "media_path": media_path,
            "wav_path": wav_path,
            "wav_path_2": wav_path_2
        }
    
    def calculate_max_frames(self, wav_path: str, wav_path_2: str = None, fps: int = 25) -> int:
        """Calculate max frames based on audio duration"""
        durations = []
        
        try:
            duration1 = librosa.get_duration(path=wav_path)
            durations.append(duration1)
            logger.info(f"Audio 1 duration: {duration1:.2f}s")
        except Exception as e:
            logger.warning(f"Failed to get audio 1 duration: {e}")
        
        if wav_path_2:
            try:
                duration2 = librosa.get_duration(path=wav_path_2)
                durations.append(duration2)
                logger.info(f"Audio 2 duration: {duration2:.2f}s")
            except Exception as e:
                logger.warning(f"Failed to get audio 2 duration: {e}")
        
        if not durations:
            logger.warning("Could not calculate audio duration, using default")
            return 81
        
        max_duration = max(durations)
        max_frames = int(max_duration * fps) + 81
        
        logger.info(f"Calculated max_frames: {max_frames} (duration: {max_duration:.2f}s, fps: {fps})")
        return max_frames
    
    def configure_workflow(self, workflow: dict, job_input: dict, media_paths: dict) -> dict:
        """Configure workflow with input parameters"""
        input_type = job_input.get("input_type", "image")
        person_count = job_input.get("person_count", "single")
        
        # Get media paths
        media_path = media_paths["media_path"]
        wav_path = media_paths["wav_path"]
        wav_path_2 = media_paths.get("wav_path_2")
        
        # Get other parameters
        prompt = job_input.get("prompt", "A person talking naturally")
        width = job_input.get("width", 512)
        height = job_input.get("height", 512)
        max_frame = job_input.get("max_frame")
        
        # Calculate max_frame if not provided
        if max_frame is None:
            max_frame = self.calculate_max_frames(wav_path, wav_path_2)
        
        logger.info(f"Workflow config: prompt='{prompt}', size={width}x{height}, frames={max_frame}")
        
        # Configure workflow nodes
        # Note: Node IDs are based on the workflow JSON structure
        
        # Copy files to ComfyUI input directory and use just filenames
        import shutil
        import os
        comfyui_input_dir = "/ComfyUI/input"
        
        # Copy and get media filename
        media_filename = os.path.basename(media_path)
        shutil.copy(media_path, os.path.join(comfyui_input_dir, media_filename))
        
        # Copy and get audio filename
        wav_filename = os.path.basename(wav_path)
        shutil.copy(wav_path, os.path.join(comfyui_input_dir, wav_filename))
        
        logger.info(f"Media filename: {media_filename}, Audio filename: {wav_filename}")
        
        # Set media input (image or video)
        if input_type == "image":
            if "284" in workflow:  # Image loader node
                workflow["284"]["inputs"]["image"] = media_filename
        else:
            if "228" in workflow:  # Video loader node
                workflow["228"]["inputs"]["video"] = media_filename
        
        # Set audio input
        if "125" in workflow:  # Audio loader node
            workflow["125"]["inputs"]["audio"] = wav_filename
        
        # Set prompt
        if "241" in workflow:  # Prompt node
            workflow["241"]["inputs"]["positive_prompt"] = prompt
        
        # Set dimensions
        if "245" in workflow:  # Width node
            workflow["245"]["inputs"]["value"] = width
        if "246" in workflow:  # Height node
            workflow["246"]["inputs"]["value"] = height
        
        # Set max frames
        if "270" in workflow:  # Max frames node
            workflow["270"]["inputs"]["value"] = max_frame
        
        # Enable save_output for Video Combine node to generate output files
        if "131" in workflow:  # VHS_VideoCombine node
            workflow["131"]["inputs"]["save_output"] = True
        
        # Set second audio for multi-person
        if person_count == "multi" and wav_path_2:
            wav_filename_2 = os.path.basename(wav_path_2)
            shutil.copy(wav_path_2, os.path.join(comfyui_input_dir, wav_filename_2))
            
            if input_type == "image":
                if "307" in workflow:  # Second audio node for I2V_multi
                    workflow["307"]["inputs"]["audio"] = wav_filename_2
            else:
                if "313" in workflow:  # Second audio node for V2V_multi
                    workflow["313"]["inputs"]["audio"] = wav_filename_2
        
        return workflow


if __name__ == "__main__":
    # Start the handler
    handler = InfiniteTalkHandler()
    start_handler(handler)
