# PowerShell script to push Docker image to Docker Hub for RunPod deployment

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Docker Hub Push Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if logged in
Write-Host "Step 1: Checking Docker login status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1 | Out-String
    if ($dockerInfo -match "Username") {
        Write-Host "✅ Already logged in to Docker Hub" -ForegroundColor Green
    } else {
        Write-Host "Not logged in to Docker Hub. Please login:" -ForegroundColor Red
        docker login
    }
} catch {
    Write-Host "Not logged in to Docker Hub. Please login:" -ForegroundColor Red
    docker login
}

Write-Host ""
Write-Host "Step 2: Image information" -ForegroundColor Yellow
docker images storystudio/infinitetalk:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

Write-Host ""
Write-Host "Step 3: Tagging image with version..." -ForegroundColor Yellow
$VERSION = "v1.0"
docker tag storystudio/infinitetalk:latest storystudio/infinitetalk:$VERSION

Write-Host ""
Write-Host "Step 4: Tagged versions:" -ForegroundColor Yellow
docker images storystudio/infinitetalk --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Ready to push!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: This image is ~102GB. Push will take significant time depending on your upload speed." -ForegroundColor Yellow
Write-Host "Estimated time: 1-3 hours on typical home internet" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Do you want to proceed with push? (y/n)"
if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
    Write-Host ""
    Write-Host "Pushing storystudio/infinitetalk:latest..." -ForegroundColor Green
    docker push storystudio/infinitetalk:latest
    
    Write-Host ""
    Write-Host "Pushing storystudio/infinitetalk:$VERSION..." -ForegroundColor Green
    docker push storystudio/infinitetalk:$VERSION
    
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "✅ Push complete!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Image available at:" -ForegroundColor Green
    Write-Host "  - storystudio/infinitetalk:latest" -ForegroundColor White
    Write-Host "  - storystudio/infinitetalk:$VERSION" -ForegroundColor White
    Write-Host ""
    Write-Host "Use in RunPod template as:" -ForegroundColor Yellow
    Write-Host "  Container Image: storystudio/infinitetalk:latest" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "Push cancelled." -ForegroundColor Yellow
}
