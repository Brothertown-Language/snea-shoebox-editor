#!/bin/bash
# Copyright (c) 2026 Brothertown Language
#
# Check GPU availability and Docker GPU support for embedding service.
#
# Usage:
#   bash scripts/check_gpu.sh

set -e

echo "=========================================="
echo "GPU Availability Check"
echo "=========================================="
echo ""

# Check for NVIDIA GPU
echo "1. Checking for NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo "   ✓ nvidia-smi found"
    echo ""
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo ""
else
    echo "   ✗ nvidia-smi not found"
    echo "   No NVIDIA GPU detected or drivers not installed"
    echo ""
    echo "   To install NVIDIA drivers:"
    echo "   - Ubuntu/Debian: sudo apt install nvidia-driver-XXX"
    echo "   - See: https://www.nvidia.com/Download/index.aspx"
    exit 1
fi

# Check for Docker
echo "2. Checking for Docker..."
if command -v docker &> /dev/null; then
    echo "   ✓ Docker found: $(docker --version)"
else
    echo "   ✗ Docker not found"
    echo "   Install Docker: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check for NVIDIA Container Toolkit
echo ""
echo "3. Checking for NVIDIA Container Toolkit..."
if docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "   ✓ NVIDIA Container Toolkit is working"
    echo ""
    echo "   Testing GPU access in Docker:"
    docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "   ✗ NVIDIA Container Toolkit not working"
    echo ""
    echo "   To install NVIDIA Container Toolkit:"
    echo "   1. Add repository:"
    echo "      distribution=\$(. /etc/os-release;echo \$ID\$VERSION_ID)"
    echo "      curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg"
    echo "      curl -s -L https://nvidia.github.io/libnvidia-container/\$distribution/libnvidia-container.list | \\"
    echo "        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \\"
    echo "        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list"
    echo ""
    echo "   2. Install:"
    echo "      sudo apt-get update"
    echo "      sudo apt-get install -y nvidia-container-toolkit"
    echo ""
    echo "   3. Configure Docker:"
    echo "      sudo nvidia-ctk runtime configure --runtime=docker"
    echo "      sudo systemctl restart docker"
    echo ""
    echo "   See: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi

# Check Docker Compose
echo ""
echo "4. Checking for Docker Compose..."
if docker compose version &> /dev/null; then
    echo "   ✓ Docker Compose found: $(docker compose version)"
elif command -v docker-compose &> /dev/null; then
    echo "   ✓ Docker Compose found: $(docker-compose --version)"
else
    echo "   ✗ Docker Compose not found"
    echo "   Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All checks passed!"
echo "=========================================="
echo ""
echo "Your system is ready to run the embedding service."
echo ""
echo "To start the embedding service:"
echo "  docker-compose up -d embeddings"
echo ""
echo "To test the embedding service:"
echo "  uv run python scripts/test_embeddings.py"
echo ""
