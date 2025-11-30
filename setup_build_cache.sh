#!/bin/bash
# Setup build cache on EC2 to avoid re-downloading everything
# Run this once on EC2 to populate cache

set -e

CACHE_DIR="$HOME/docker_build_cache"
mkdir -p "$CACHE_DIR"/{models,repos,pip}

echo "=========================================="
echo "Setting up Docker Build Cache"
echo "Cache Directory: $CACHE_DIR"
echo "=========================================="

# Create pip cache directory
export PIP_CACHE_DIR="$CACHE_DIR/pip"

# Download ComfyUI if not cached
if [ ! -d "$CACHE_DIR/repos/ComfyUI" ]; then
    echo "Caching ComfyUI repository..."
    cd "$CACHE_DIR/repos"
    git clone https://github.com/comfyanonymous/ComfyUI.git
else
    echo "✓ ComfyUI already cached"
fi

# Download custom nodes repositories
CUSTOM_NODES=(
    "ltdrdata/ComfyUI-Manager"
    "city96/ComfyUI-GGUF"
    "kijai/ComfyUI-KJNodes"
    "Kosinkadink/ComfyUI-VideoHelperSuite"
    "wanpang/ComfyUI-wanBlockswap"
    "ZHO-ZHO-ZHO/ComfyUI-MelBandRoFormer"
    "AlexYapp/ComfyUI-WanVideoWrapper"
)

for node in "${CUSTOM_NODES[@]}"; do
    node_name=$(basename "$node")
    if [ ! -d "$CACHE_DIR/repos/$node_name" ]; then
        echo "Caching $node_name..."
        cd "$CACHE_DIR/repos"
        git clone "https://github.com/$node.git"
    else
        echo "✓ $node_name already cached"
    fi
done

# Download models using huggingface-cli
echo "Setting up model cache..."
mkdir -p "$CACHE_DIR/models"

# Create a text file with model URLs for reference
cat > "$CACHE_DIR/models/model_sources.txt" << 'EOF'
# InfiniteTalk Models - Download these manually or via huggingface-cli

## Main Models (Large - download separately if needed)
https://huggingface.co/wanpang/Wan2_1_InfiniteTalk_Single/resolve/main/Wan2_1-InfiniteTalk_Single_Q8.gguf
https://huggingface.co/wanpang/wan2.1-i2v-14b-480p/resolve/main/wan2.1-i2v-14b-480p-Q8_0.gguf

## Audio Model
https://huggingface.co/TencentGameMate/chinese-wav2vec2-base

## Text Encoder
https://huggingface.co/TencentGameMate/t5-small-chinese-en

## Clip Vision
https://huggingface.co/wanpang/chinese-clip-vit-large-patch14-336px

## Safetensors
https://huggingface.co/wanpang/chinese-clip-vit-large-patch14-336px/resolve/main/model.safetensors
https://huggingface.co/wanpang/chinese-clip-vit-large-patch14-336px/resolve/main/preprocessor_config.json
EOF

echo ""
echo "=========================================="
echo "Cache Setup Complete!"
echo "=========================================="
echo "Cache location: $CACHE_DIR"
echo ""
echo "NOTE: Large model files need to be downloaded manually."
echo "See $CACHE_DIR/models/model_sources.txt for URLs"
echo ""
echo "To download models, run:"
echo "  cd $CACHE_DIR/models"
echo "  wget <model_url>"
echo ""
