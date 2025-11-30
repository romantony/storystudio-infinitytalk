#!/bin/bash
# Build script for using cached resources
# Run this on EC2 instead of docker build directly

set -e

CACHE_DIR="$HOME/docker_build_cache"
BUILD_DIR="$HOME/storystudio-infinitytalk"

echo "=========================================="
echo "Building Docker Image with Cache"
echo "=========================================="

# Create temporary build context
TEMP_BUILD="$BUILD_DIR/build_temp"
rm -rf "$TEMP_BUILD"
mkdir -p "$TEMP_BUILD/cache/repos"

# Copy cached repos to build context
if [ -d "$CACHE_DIR/repos" ]; then
    echo "Copying cached repositories..."
    cp -r "$CACHE_DIR/repos"/* "$TEMP_BUILD/cache/repos/"
else
    echo "ERROR: Cache not found. Run setup_build_cache.sh first"
    exit 1
fi

# Build with cached Dockerfile
cd "$BUILD_DIR"
docker build -f Dockerfile -t romantony/storystudio-infinitetalk:v1.8 .

# Cleanup
rm -rf "$TEMP_BUILD"

echo "=========================================="
echo "Build Complete!"
echo "=========================================="
