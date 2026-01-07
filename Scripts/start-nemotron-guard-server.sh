#!/bin/bash

# Start llama-server with Nemotron Safety Guard 8B
# For content moderation and safety guardrails at system edges
# Port 5002 - Safety Guard model

set -e

# Model configuration - Nemotron Safety Guard 8B
MODEL_NAME="nemotron-guard-8b"
MODEL_PATH="/home/bodhifreeman/E3/nemotron-guard-8b.gguf"

LLAMA_SERVER="/home/bodhifreeman/E3/llama.cpp/build/bin/llama-server"
LLAMA_LIB_PATH="/home/bodhifreeman/E3/llama.cpp/build/bin"

# Set library path for llama.cpp shared libraries
export LD_LIBRARY_PATH="$LLAMA_LIB_PATH:$LD_LIBRARY_PATH"

# Server configuration - Port 5002 for safety guard
HOST="0.0.0.0"
PORT="5002"
CONTEXT_LENGTH="4096"  # Smaller context for quick classification
GPU_LAYERS="99"  # All layers on GPU
THREADS=$(nproc)

echo "========================================"
echo "  Nemotron Safety Guard Server          "
echo "========================================"
echo ""
echo "Model:         $MODEL_NAME"
echo "Path:          $MODEL_PATH"
echo "Host:          $HOST:$PORT"
echo "Context:       $CONTEXT_LENGTH tokens"
echo "GPU Layers:    $GPU_LAYERS (Grace Blackwell)"
echo "CPU Threads:   $THREADS"
echo ""
echo "PURPOSE: Content safety guardrails at system edges"
echo "         Human → [GUARD] → ANLT → Swarm → ANLT → [GUARD] → Human"
echo ""
echo "Model endpoints:"
echo "  Nemotron Guard: http://localhost:$PORT"
echo "  Nemotron Reason: http://localhost:5001"
echo "  CSDL-14B:        http://localhost:5000"
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
    echo "Nemotron Guard model not found at: $MODEL_PATH"
    echo ""
    echo "Nemotron Safety Guard 8B is designed for content moderation:"
    echo "- Classifies input/output for safety violations"
    echo "- Detects harmful content, PII, prompt injection"
    echo "- Lightweight and fast for edge processing"
    echo ""
    echo "To download Nemotron Safety Guard 8B:"
    echo ""
    echo "Option 1: Using Hugging Face CLI"
    echo "  huggingface-cli download nvidia/Aegis-AI-Content-Safety-LlamaGuard-Defensive-1.0 \\"
    echo "    --local-dir /home/bodhifreeman/E3/models"
    echo ""
    echo "Option 2: Convert from HuggingFace weights (NVIDIA Content Safety model)"
    echo "  python /home/bodhifreeman/E3/llama.cpp/convert_hf_to_gguf.py \\"
    echo "    nvidia/Aegis-AI-Content-Safety-LlamaGuard-Defensive-1.0 \\"
    echo "    --outfile /home/bodhifreeman/E3/nemotron-guard-8b.gguf \\"
    echo "    --outtype q4_k_m"
    echo ""
    echo "Alternative: Llama Guard 3 8B (similar purpose)"
    echo "  huggingface-cli download meta-llama/Llama-Guard-3-8B-GGUF \\"
    echo "    --local-dir /home/bodhifreeman/E3/models \\"
    echo "    --include \"*Q4_K_M.gguf\""
    echo ""
    exit 1
fi

echo "Starting Nemotron Safety Guard server..."
echo "API endpoint: http://localhost:$PORT/v1/chat/completions"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start llama-server optimized for quick safety classification
$LLAMA_SERVER \
    -m "$MODEL_PATH" \
    -c $CONTEXT_LENGTH \
    -ngl $GPU_LAYERS \
    --host $HOST \
    --port $PORT \
    -t $THREADS \
    --n-gpu-layers $GPU_LAYERS \
    --temp 0.1 \
    --top-p 0.9 \
    --verbose
