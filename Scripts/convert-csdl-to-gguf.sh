#!/bin/bash

# Convert CSDL-14B SafeTensors to GGUF F16 format
# This script will be run once the model copy is complete

set -e

MODEL_INPUT="/home/bodhifreeman/E3/model-training/model/merged_16bit"
MODEL_OUTPUT="/home/bodhifreeman/E3/csdl-14b-f16.gguf"
LLAMA_CPP_DIR="/home/bodhifreeman/E3/llama.cpp"

echo "=== CSDL-14B to GGUF Conversion ==="
echo "Input:  $MODEL_INPUT"
echo "Output: $MODEL_OUTPUT"
echo ""

# Check if model files exist
if [ ! -d "$MODEL_INPUT" ]; then
    echo "Error: Model directory not found: $MODEL_INPUT"
    exit 1
fi

# Check if all 6 safetensors files are present
SAFETENSORS_COUNT=$(ls $MODEL_INPUT/model-*.safetensors 2>/dev/null | wc -l)
if [ "$SAFETENSORS_COUNT" -ne 6 ]; then
    echo "Error: Expected 6 safetensors files, found $SAFETENSORS_COUNT"
    echo "Please wait for the model copy to complete."
    exit 1
fi

echo "All 6 safetensors files found ✓"
echo ""

# Check if llama.cpp is built
if [ ! -f "$LLAMA_CPP_DIR/build/bin/llama-server" ]; then
    echo "Error: llama.cpp not built. Please run the build first."
    exit 1
fi

echo "Starting conversion to GGUF F16..."
echo "This may take 10-15 minutes..."
echo ""

# Convert to GGUF (using venv)
source $LLAMA_CPP_DIR/venv/bin/activate
python3 $LLAMA_CPP_DIR/convert_hf_to_gguf.py \
    $MODEL_INPUT \
    --outfile $MODEL_OUTPUT \
    --outtype f16
deactivate

echo ""
echo "=== Conversion Complete! ==="
echo "GGUF model saved to: $MODEL_OUTPUT"
echo ""

# Show file size
echo "Model size: $(du -h $MODEL_OUTPUT | cut -f1)"
echo ""
echo "You can now run llama-server with:"
echo "  ./llama.cpp/build/bin/llama-server -m $MODEL_OUTPUT -c 4096 -ngl 99 --host 0.0.0.0 --port 8002"
