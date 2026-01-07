#!/bin/bash

# Start llama-server with Nemotron Nano model for reasoning
# Designed for DGX Spark (128GB unified memory, Grace Blackwell)
# Port 5001 - Reasoning model (CSDL-14B runs on port 5000)

set -e

# Model configuration
# Nemotron Nano 8B is optimized for DGX Spark with NVFP4 quantization
# If you have the 30B variant, update this path
MODEL_NAME="nemotron-nano-8b"
MODEL_PATH="/home/bodhifreeman/E3/nemotron-nano-8b.gguf"
ALT_MODEL_PATH="/home/bodhifreeman/E3/nemotron-nano-30b.gguf"

LLAMA_SERVER="/home/bodhifreeman/E3/llama.cpp/build/bin/llama-server"
LLAMA_LIB_PATH="/home/bodhifreeman/E3/llama.cpp/build/bin"

# Set library path for llama.cpp shared libraries
export LD_LIBRARY_PATH="$LLAMA_LIB_PATH:$LD_LIBRARY_PATH"

# Server configuration - Port 5001 for reasoning model
HOST="0.0.0.0"
PORT="5001"
CONTEXT_LENGTH="8192"  # Larger context for reasoning
GPU_LAYERS="99"  # All layers on GPU
THREADS=$(nproc)

# Check for alternative model path (30B variant)
if [ ! -f "$MODEL_PATH" ] && [ -f "$ALT_MODEL_PATH" ]; then
    MODEL_PATH="$ALT_MODEL_PATH"
    MODEL_NAME="nemotron-nano-30b"
fi

echo "========================================"
echo "  Nemotron Reasoning Server (HYBRID)   "
echo "========================================"
echo ""
echo "Model:         $MODEL_NAME"
echo "Path:          $MODEL_PATH"
echo "Host:          $HOST:$PORT"
echo "Context:       $CONTEXT_LENGTH tokens"
echo "GPU Layers:    $GPU_LAYERS (Grace Blackwell)"
echo "CPU Threads:   $THREADS"
echo ""
echo "Architecture:  Nemotron(reason) → CSDL-14B(encode)"
echo "CSDL Server:   http://localhost:5000"
echo "Nemotron Server: http://localhost:$PORT"
echo ""

# Check if llama-server is built
if [ ! -f "$LLAMA_SERVER" ]; then
    echo "Error: llama-server not found: $LLAMA_SERVER"
    echo "Please complete the llama.cpp build first"
    exit 1
fi

# Check if model exists, provide download instructions if not
if [ ! -f "$MODEL_PATH" ]; then
    echo "=========================================="
    echo "  Model not found - Download Required    "
    echo "=========================================="
    echo ""
    echo "Nemotron GGUF model not found at: $MODEL_PATH"
    echo ""
    echo "To download Nemotron Nano 8B (recommended for DGX Spark):"
    echo ""
    echo "Option 1: Using Hugging Face CLI"
    echo "  huggingface-cli download nvidia/Nemotron-Nano-8B-Instruct-GGUF \\"
    echo "    --local-dir /home/bodhifreeman/E3/models \\"
    echo "    --include \"*Q4_K_M.gguf\""
    echo ""
    echo "Option 2: Direct download (if available)"
    echo "  cd /home/bodhifreeman/E3"
    echo "  wget https://huggingface.co/nvidia/Nemotron-Nano-8B-Instruct-GGUF/resolve/main/nemotron-nano-8b-Q4_K_M.gguf"
    echo "  mv nemotron-nano-8b-Q4_K_M.gguf nemotron-nano-8b.gguf"
    echo ""
    echo "Option 3: Convert from HuggingFace weights"
    echo "  python /home/bodhifreeman/E3/llama.cpp/convert_hf_to_gguf.py \\"
    echo "    nvidia/Nemotron-Nano-8B-Instruct \\"
    echo "    --outfile /home/bodhifreeman/E3/nemotron-nano-8b.gguf \\"
    echo "    --outtype f16"
    echo ""
    echo "For Nemotron Nano 30B (if available):"
    echo "  Similar process with nvidia/Nemotron-Nano-30B-Instruct"
    echo ""
    exit 1
fi

echo "Starting Nemotron reasoning server..."
echo "API endpoint: http://localhost:$PORT/v1/chat/completions"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start llama-server optimized for Grace Blackwell
# Nemotron uses a specific chat template
$LLAMA_SERVER \
    -m "$MODEL_PATH" \
    -c $CONTEXT_LENGTH \
    -ngl $GPU_LAYERS \
    --host $HOST \
    --port $PORT \
    -t $THREADS \
    --n-gpu-layers $GPU_LAYERS \
    --temp 0.7 \
    --top-p 0.9 \
    --verbose
