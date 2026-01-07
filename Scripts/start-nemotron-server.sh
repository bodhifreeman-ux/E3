#!/bin/bash

# Start llama-server with Nemotron 3 Nano 30B for reasoning
# Cognitive Architecture: Nemotron (reasoning) + CSDL-14B (encoding)
# Designed for DGX Spark (128GB unified memory, Grace Blackwell)
# Port 5001 - Reasoning model (CSDL-14B runs on port 5000)

set -e

# Model configuration - Nemotron 3 Nano 30B (MoE - 3.5B active)
MODEL_NAME="nemotron-3-nano-30b"
MODEL_PATH="/home/bodhifreeman/E3/models/Nemotron-3-Nano-30B-A3B-Q6_K.gguf"

LLAMA_SERVER="/home/bodhifreeman/E3/llama.cpp/build/bin/llama-server"
LLAMA_LIB_PATH="/home/bodhifreeman/E3/llama.cpp/build/bin"

# Set library path for llama.cpp shared libraries
export LD_LIBRARY_PATH="$LLAMA_LIB_PATH:$LD_LIBRARY_PATH"

# Server configuration - Port 5001 for reasoning model
HOST="0.0.0.0"
PORT="5001"
CONTEXT_LENGTH="32768"  # 32K context (model supports up to 1M)
GPU_LAYERS="99"  # All layers on GPU
THREADS=$(nproc)

echo "=============================================="
echo "  Nemotron 3 Nano 30B - Cognitive Reasoning   "
echo "=============================================="
echo ""
echo "Model:         $MODEL_NAME"
echo "Architecture:  MoE (30B total, 3.5B active)"
echo "Path:          $MODEL_PATH"
echo "Host:          $HOST:$PORT"
echo "Context:       $CONTEXT_LENGTH tokens"
echo "GPU Layers:    $GPU_LAYERS (Grace Blackwell)"
echo "CPU Threads:   $THREADS"
echo ""
echo "Cognitive Architecture:"
echo "  Nemotron (reason) -> CSDL-14B (encode) -> CSDL Bus"
echo ""
echo "Endpoints:"
echo "  Nemotron:  http://localhost:$PORT"
echo "  CSDL-14B:  http://localhost:5000"
echo ""

# Check if llama-server is built
if [ ! -f "$LLAMA_SERVER" ]; then
    echo "Error: llama-server not found: $LLAMA_SERVER"
    echo "Please complete the llama.cpp build first"
    exit 1
fi

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "=========================================="
    echo "  Model not found - Download Required    "
    echo "=========================================="
    echo ""
    echo "Model not found at: $MODEL_PATH"
    echo ""
    echo "Download Nemotron 3 Nano 30B Q6_K (33.5GB):"
    echo ""
    echo "  huggingface-cli download unsloth/Nemotron-3-Nano-30B-A3B-GGUF \\"
    echo "    Nemotron-3-Nano-30B-A3B-Q6_K.gguf \\"
    echo "    --local-dir /home/bodhifreeman/E3/models"
    echo ""
    exit 1
fi

echo "Starting Nemotron 3 Nano 30B reasoning server..."
echo "API endpoint: http://localhost:$PORT/v1/chat/completions"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start llama-server optimized for Grace Blackwell
# Nemotron 3 uses <think></think> tokens for reasoning
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
    --special \
    --verbose
