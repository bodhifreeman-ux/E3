#!/bin/bash
# Build PyTorch with CUDA 13.0 for Grace Blackwell GB10
# Optimized for ARM64 architecture

set -e

echo "=== Building PyTorch with CUDA 13.0 for Grace Blackwell ==="
echo "This will take 2-4 hours. Go grab a coffee (or several)."
echo ""

# System info
echo "System: $(uname -m)"
echo "CUDA Version: $(nvcc --version | grep release)"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
echo ""

# Install build dependencies
echo "Installing build dependencies..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    ninja-build \
    ccache \
    libopenblas-dev \
    liblapack-dev \
    python3-dev \
    python3-pip \
    python3-venv

# Create build directory
BUILD_DIR="/home/bodhifreeman/pytorch-build"
mkdir -p $BUILD_DIR
cd $BUILD_DIR

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv pytorch-venv
source pytorch-venv/bin/activate

# Install Python dependencies
echo "Installing Python build dependencies..."
pip install --upgrade pip setuptools wheel
pip install numpy pyyaml mkl mkl-include setuptools cmake cffi typing_extensions

# Clone PyTorch (stable release)
if [ ! -d "pytorch" ]; then
    echo "Cloning PyTorch..."
    git clone --recursive https://github.com/pytorch/pytorch.git
    cd pytorch
    git checkout v2.5.1  # Latest stable
    git submodule sync
    git submodule update --init --recursive
else
    echo "PyTorch already cloned, updating..."
    cd pytorch
    git pull
    git submodule update --init --recursive
fi

# Set environment variables for Grace Blackwell (SM 121a)
export CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which python))/../"}
export USE_CUDA=1
export USE_CUDNN=1
export CUDA_HOME=/usr/local/cuda-13.0
export TORCH_CUDA_ARCH_LIST="12.1"  # Blackwell compute capability
export MAX_JOBS=$(nproc)
export USE_SYSTEM_NCCL=0
export BUILD_CAFFE2=0  # Don't need Caffe2
export USE_DISTRIBUTED=1
export USE_NCCL=1
export USE_MKLDNN=1

# Enable ccache for faster rebuilds
export USE_CCACHE=1
export CCACHE_DIR=/home/bodhifreeman/.ccache

echo ""
echo "Build configuration:"
echo "  CUDA: $USE_CUDA"
echo "  CUDA_HOME: $CUDA_HOME"
echo "  Arch List: $TORCH_CUDA_ARCH_LIST"
echo "  Max Jobs: $MAX_JOBS"
echo ""

# Clean previous build
python setup.py clean

# Build PyTorch
echo "Starting PyTorch build (this will take 2-4 hours)..."
echo "Build log: /tmp/pytorch-build.log"

python setup.py install 2>&1 | tee /tmp/pytorch-build.log

echo ""
echo "=== Build Complete! ==="
echo ""
echo "Testing PyTorch CUDA support..."
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo ""
echo "Virtual environment location: $BUILD_DIR/pytorch-venv"
echo "To use: source $BUILD_DIR/pytorch-venv/bin/activate"
echo ""
echo "Now install Transformers and Accelerate:"
echo "  pip install transformers accelerate"
