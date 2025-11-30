# Combined Dockerfile for InfiniteTalk RunPod Serverless
# This builds everything in one stage for easier deployment

FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Metadata
LABEL maintainer="StoryStudio Team"
LABEL model="infinitetalk"
LABEL description="InfiniteTalk AI model for lip-sync video generation"

# Remove any third-party apt sources
RUN rm -f /etc/apt/sources.list.d/*.list

# Set shell and environment variables
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV SHELL=/bin/bash
ENV CUDA_HOME=/usr/local/cuda
ENV PATH="/usr/local/cuda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

# Set working directory
WORKDIR /

# Update system and install common dependencies
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt install --yes --no-install-recommends \
    git \
    wget \
    curl \
    bash \
    libgl1 \
    software-properties-common \
    openssh-server \
    nginx \
    rsync \
    ffmpeg \
    build-essential \
    ca-certificates && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.10
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Update alternatives to make python3.10 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install NumPy 1.x first (required for compatibility)
RUN pip install --no-cache-dir "numpy<2.0.0"

# Install common Python packages
RUN pip install --no-cache-dir \
    opencv-python-headless \
    pillow \
    scipy \
    scikit-image \
    matplotlib \
    tqdm \
    psutil \
    packaging \
    pyyaml \
    requests \
    websocket-client \
    boto3 \
    librosa \
    soundfile \
    runpod

# Install ComfyUI
WORKDIR /
RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    cd /ComfyUI && \
    pip install --no-cache-dir -r requirements.txt

# Install PyTorch 2.5.1 AFTER ComfyUI (required for torch.nn.RMSNorm and secure torch.load)
# This MUST be after ComfyUI requirements to prevent it from being overwritten
# Using latest available PyTorch for CUDA 12.1 (2.5.1) - 2.6.0 not yet released for CUDA 12.1
RUN pip install --no-cache-dir --force-reinstall \
    torch==2.5.1 \
    torchvision==0.20.1 \
    torchaudio==2.5.1 \
    --index-url https://download.pytorch.org/whl/cu121

# Create necessary directories
RUN mkdir -p \
    /ComfyUI/models/checkpoints \
    /ComfyUI/models/vae \
    /ComfyUI/models/loras \
    /ComfyUI/models/embeddings \
    /ComfyUI/models/upscale_models \
    /ComfyUI/models/clip \
    /ComfyUI/models/clip_vision \
    /ComfyUI/models/diffusion_models \
    /ComfyUI/models/text_encoders \
    /ComfyUI/custom_nodes \
    /ComfyUI/input \
    /ComfyUI/output \
    /workflows \
    /base \
    /examples

# Copy base utilities
COPY base/utils/ /base/utils/
COPY base/handler_base.py /base/handler_base.py

# Install model-specific custom nodes for ComfyUI
RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/Comfy-Org/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    pip install --no-cache-dir -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/city96/ComfyUI-GGUF && \
    cd ComfyUI-GGUF && \
    pip install --no-cache-dir -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-KJNodes && \
    cd ComfyUI-KJNodes && \
    pip install --no-cache-dir -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite && \
    cd ComfyUI-VideoHelperSuite && \
    pip install --no-cache-dir -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/orssorbit/ComfyUI-wanBlockswap

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-MelBandRoFormer && \
    cd ComfyUI-MelBandRoFormer && \
    pip install --no-cache-dir -r requirements.txt

RUN cd /ComfyUI/custom_nodes && \
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper && \
    cd ComfyUI-WanVideoWrapper && \
    pip install --no-cache-dir -r requirements.txt

# Create model directories if they don't exist
RUN mkdir -p /ComfyUI/models/diffusion_models /ComfyUI/models/loras /ComfyUI/models/vae \
    /ComfyUI/models/text_encoders /ComfyUI/models/clip_vision

# Download model weights
RUN wget https://huggingface.co/Kijai/WanVideo_comfy_GGUF/resolve/main/InfiniteTalk/Wan2_1-InfiniteTalk_Single_Q8.gguf \
    -O /ComfyUI/models/diffusion_models/Wan2_1-InfiniteTalk_Single_Q8.gguf

RUN wget https://huggingface.co/Kijai/WanVideo_comfy_GGUF/resolve/main/InfiniteTalk/Wan2_1-InfiniteTalk_Multi_Q8.gguf \
    -O /ComfyUI/models/diffusion_models/Wan2_1-InfiniteTalk_Multi_Q8.gguf

RUN wget https://huggingface.co/city96/Wan2.1-I2V-14B-480P-gguf/resolve/main/wan2.1-i2v-14b-480p-Q8_0.gguf \
    -O /ComfyUI/models/diffusion_models/wan2.1-i2v-14b-480p-Q8_0.gguf

RUN wget https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors \
    -O /ComfyUI/models/loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors

RUN wget https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan2_1_VAE_bf16.safetensors \
    -O /ComfyUI/models/vae/Wan2_1_VAE_bf16.safetensors

RUN wget https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/umt5-xxl-enc-bf16.safetensors \
    -O /ComfyUI/models/text_encoders/umt5-xxl-enc-bf16.safetensors

RUN wget https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors \
    -O /ComfyUI/models/clip_vision/clip_vision_h.safetensors

RUN wget https://huggingface.co/Kijai/MelBandRoFormer_comfy/resolve/main/MelBandRoformer_fp16.safetensors \
    -O /ComfyUI/models/diffusion_models/MelBandRoformer_fp16.safetensors

# Copy workflow files
COPY models/infinitetalk/workflows/ /workflows/

# Copy handler
COPY models/infinitetalk/handler.py /handler.py

# Copy example files
COPY models/infinitetalk/examples/ /examples/

# Copy and set entrypoint
COPY base/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set working directory
WORKDIR /

# Expose ComfyUI port
EXPOSE 8188

# Start the handler
CMD ["/entrypoint.sh"]
