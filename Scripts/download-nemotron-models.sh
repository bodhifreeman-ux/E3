#!/bin/bash

# Download Nemotron models for E3 DevMind hybrid architecture
# Optimized for DGX Spark (128GB unified memory, Grace Blackwell)

set -e

E3_DIR="/home/bodhifreeman/E3"
MODELS_DIR="$E3_DIR/models"
LLAMA_CPP_DIR="$E3_DIR/llama.cpp"

echo "========================================"
echo "  Nemotron Model Downloader for E3     "
echo "========================================"
echo ""

# Create models directory if needed
mkdir -p "$MODELS_DIR"

# Check if huggingface-cli is available
if ! command -v huggingface-cli &> /dev/null; then
    echo "Installing huggingface_hub..."
    pip install huggingface_hub
fi

echo ""
echo "Which model would you like to download?"
echo ""
echo "1) Nemotron Nano 8B V2 (Recommended - ~5GB GGUF)"
echo "   - Best for DGX Spark performance (~33 tok/s)"
echo "   - High-quality reasoning for agent tasks"
echo ""
echo "2) Nemotron Safety Guard 8B (~5GB GGUF)"
echo "   - Content safety guardrails"
echo "   - Input/output moderation at system edges"
echo ""
echo "3) Both models"
echo ""
echo "4) Download from source and convert (requires more disk space)"
echo ""

read -p "Enter choice [1-4]: " choice

download_nemotron_nano() {
    echo ""
    echo "=== Downloading Nemotron Nano 8B V2 ==="
    echo ""

    # Try NVIDIA's official GGUF if available
    echo "Attempting to download pre-quantized GGUF..."

    # Method 1: Try NVIDIA's official repo (check if GGUF exists)
    if huggingface-cli download nvidia/Nemotron-Nano-8B-v2-Instruct-GGUF \
        --local-dir "$MODELS_DIR/nemotron-nano" \
        --include "*Q4_K_M.gguf" 2>/dev/null; then

        # Move/rename the GGUF file
        GGUF_FILE=$(find "$MODELS_DIR/nemotron-nano" -name "*.gguf" | head -1)
        if [ -n "$GGUF_FILE" ]; then
            mv "$GGUF_FILE" "$E3_DIR/nemotron-nano-8b.gguf"
            echo "SUCCESS: Nemotron Nano 8B downloaded to $E3_DIR/nemotron-nano-8b.gguf"
            return 0
        fi
    fi

    # Method 2: Download full model and convert
    echo ""
    echo "Pre-quantized GGUF not found. Downloading full model and converting..."
    echo "This requires ~16GB disk space temporarily."
    echo ""

    # Download the full model
    huggingface-cli download nvidia/Nemotron-Nano-8B-v2-Instruct \
        --local-dir "$MODELS_DIR/nemotron-nano-hf"

    # Convert to GGUF
    echo ""
    echo "Converting to GGUF format..."
    python3 "$LLAMA_CPP_DIR/convert_hf_to_gguf.py" \
        "$MODELS_DIR/nemotron-nano-hf" \
        --outfile "$E3_DIR/nemotron-nano-8b.gguf" \
        --outtype q4_k_m

    echo ""
    echo "SUCCESS: Nemotron Nano 8B converted to $E3_DIR/nemotron-nano-8b.gguf"

    # Cleanup HF weights to save space
    read -p "Remove HuggingFace weights to save space? [y/N]: " cleanup
    if [[ "$cleanup" =~ ^[Yy]$ ]]; then
        rm -rf "$MODELS_DIR/nemotron-nano-hf"
        echo "Cleaned up HuggingFace weights."
    fi
}

download_safety_guard() {
    echo ""
    echo "=== Downloading Nemotron Safety Guard 8B ==="
    echo ""

    # NVIDIA Aegis Content Safety model
    echo "Downloading NVIDIA Aegis Content Safety model..."

    # Method 1: Try GGUF version
    if huggingface-cli download nvidia/Aegis-AI-Content-Safety-LlamaGuard-Defensive-1.0-GGUF \
        --local-dir "$MODELS_DIR/nemotron-guard" \
        --include "*Q4_K_M.gguf" 2>/dev/null; then

        GGUF_FILE=$(find "$MODELS_DIR/nemotron-guard" -name "*.gguf" | head -1)
        if [ -n "$GGUF_FILE" ]; then
            mv "$GGUF_FILE" "$E3_DIR/nemotron-guard-8b.gguf"
            echo "SUCCESS: Nemotron Guard 8B downloaded to $E3_DIR/nemotron-guard-8b.gguf"
            return 0
        fi
    fi

    # Method 2: Download and convert
    echo ""
    echo "Pre-quantized GGUF not found. Downloading full model and converting..."

    huggingface-cli download nvidia/Aegis-AI-Content-Safety-LlamaGuard-Defensive-1.0 \
        --local-dir "$MODELS_DIR/nemotron-guard-hf"

    echo ""
    echo "Converting to GGUF format..."
    python3 "$LLAMA_CPP_DIR/convert_hf_to_gguf.py" \
        "$MODELS_DIR/nemotron-guard-hf" \
        --outfile "$E3_DIR/nemotron-guard-8b.gguf" \
        --outtype q4_k_m

    echo ""
    echo "SUCCESS: Nemotron Guard 8B converted to $E3_DIR/nemotron-guard-8b.gguf"

    read -p "Remove HuggingFace weights to save space? [y/N]: " cleanup
    if [[ "$cleanup" =~ ^[Yy]$ ]]; then
        rm -rf "$MODELS_DIR/nemotron-guard-hf"
        echo "Cleaned up HuggingFace weights."
    fi
}

case $choice in
    1)
        download_nemotron_nano
        ;;
    2)
        download_safety_guard
        ;;
    3)
        download_nemotron_nano
        download_safety_guard
        ;;
    4)
        echo ""
        echo "Manual conversion mode. Run the following commands:"
        echo ""
        echo "# For Nemotron Nano 8B:"
        echo "huggingface-cli download nvidia/Nemotron-Nano-8B-v2-Instruct --local-dir $MODELS_DIR/nemotron-nano-hf"
        echo "python3 $LLAMA_CPP_DIR/convert_hf_to_gguf.py $MODELS_DIR/nemotron-nano-hf --outfile $E3_DIR/nemotron-nano-8b.gguf --outtype q4_k_m"
        echo ""
        echo "# For Safety Guard:"
        echo "huggingface-cli download nvidia/Aegis-AI-Content-Safety-LlamaGuard-Defensive-1.0 --local-dir $MODELS_DIR/nemotron-guard-hf"
        echo "python3 $LLAMA_CPP_DIR/convert_hf_to_gguf.py $MODELS_DIR/nemotron-guard-hf --outfile $E3_DIR/nemotron-guard-8b.gguf --outtype q4_k_m"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "  Model Download Complete              "
echo "========================================"
echo ""
echo "Models downloaded to $E3_DIR:"
ls -lh "$E3_DIR"/*.gguf 2>/dev/null || echo "No GGUF files found yet"
echo ""
echo "Next steps:"
echo "1. Start CSDL-14B:        ./Scripts/start-llama-server.sh"
echo "2. Start Nemotron Nano:   ./Scripts/start-nemotron-server.sh"
echo "3. Start Safety Guard:    ./Scripts/start-nemotron-guard-server.sh"
echo "4. Start E3 DevMind:      ./Scripts/start-e3-devmind-swarm.sh"
echo ""
