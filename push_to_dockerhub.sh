#!/bin/bash
# Script to push Docker image to Docker Hub for RunPod deployment

echo "=================================="
echo "Docker Hub Push Script"
echo "=================================="
echo ""

# Check if logged in
echo "Step 1: Checking Docker login status..."
if ! docker info | grep -q "Username"; then
    echo "Not logged in to Docker Hub. Please login:"
    docker login
else
    echo "✅ Already logged in to Docker Hub"
fi

echo ""
echo "Step 2: Image information"
docker images storystudio/infinitetalk:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "Step 3: Tagging image with version..."
VERSION="v1.0"
docker tag storystudio/infinitetalk:latest storystudio/infinitetalk:$VERSION

echo ""
echo "Step 4: Tagged versions:"
docker images storystudio/infinitetalk --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "=================================="
echo "Ready to push!"
echo "=================================="
echo ""
echo "Note: This image is ~102GB. Push will take significant time depending on your upload speed."
echo "Estimated time: 1-3 hours on typical home internet"
echo ""
read -p "Do you want to proceed with push? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "Pushing storystudio/infinitetalk:latest..."
    docker push storystudio/infinitetalk:latest
    
    echo ""
    echo "Pushing storystudio/infinitetalk:$VERSION..."
    docker push storystudio/infinitetalk:$VERSION
    
    echo ""
    echo "=================================="
    echo "✅ Push complete!"
    echo "=================================="
    echo ""
    echo "Image available at:"
    echo "  - storystudio/infinitetalk:latest"
    echo "  - storystudio/infinitetalk:$VERSION"
    echo ""
    echo "Use in RunPod template as:"
    echo "  Container Image: storystudio/infinitetalk:latest"
else
    echo ""
    echo "Push cancelled."
fi
