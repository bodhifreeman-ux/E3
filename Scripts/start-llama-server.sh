#!/bin/bash

# Start llama-server with CSDL-14B model
# Optimized for NVIDIA Grace Blackwell GPU

set -e

MODEL_PATH="/home/bodhifreeman/E3/E3/csdl-14b-f16.gguf"
LLAMA_SERVER="/home/bodhifreeman/E3/E3/llama.cpp/build/bin/llama-server"

# Server configuration
HOST="0.0.0.0"
PORT="8002"
CONTEXT_LENGTH="4096"
GPU_LAYERS="99"  # All layers on GPU
THREADS=$(nproc)

echo "=== Starting llama-server with CSDL-14B ==="
echo "Model:         $MODEL_PATH"
echo "Host:          $HOST:$PORT"
echo "Context:       $CONTEXT_LENGTH tokens"
echo "GPU Layers:    $GPU_LAYERS (all on Grace Blackwell)"
echo "CPU Threads:   $THREADS"
echo ""

# Check if model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model not found: $MODEL_PATH"
    echo "Please run ./convert-csdl-to-gguf.sh first"
    exit 1
fi

# Check if llama-server is built
if [ ! -f "$LLAMA_SERVER" ]; then
    echo "Error: llama-server not found: $LLAMA_SERVER"
    echo "Please complete the llama.cpp build first"
    exit 1
fi

echo "Starting server..."
echo "Access the server at: http://localhost:$PORT"
echo "API endpoint: http://localhost:$PORT/v1/chat/completions"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start llama-server with optimized settings for Grace Blackwell
# CRITICAL: Force chatml format to prevent Hermes 2 Pro misdetection
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
    --chat-template chatml \
    --verbose
