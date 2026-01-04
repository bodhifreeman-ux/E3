# Installation Guide

This guide covers installing and setting up CSDL-14B on your local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Install with Ollama](#quick-install-with-ollama)
3. [Manual Installation](#manual-installation)
4. [Installing LoRA Adapters](#installing-lora-adapters)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware Requirements

| Configuration | RAM | GPU VRAM | Storage |
|--------------|-----|----------|---------|
| Minimum (Q4_K_M) | 12 GB | 8 GB | 15 GB |
| Recommended (Q4_K_M) | 16 GB | 10 GB | 20 GB |
| Full Precision (FP16) | 32 GB | 24 GB | 35 GB |

### Software Requirements

- **Operating System**: Linux, macOS, or Windows (WSL2)
- **Ollama**: Version 0.1.0 or later
- **Git LFS**: For downloading model files (optional)

## Quick Install with Ollama

### Step 1: Install Ollama

**Linux/WSL:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from [ollama.com/download](https://ollama.com/download)

### Step 2: Start Ollama

```bash
ollama serve
```

### Step 3: Pull the Model

```bash
# Base model (recommended)
ollama pull lubtfy/csdl-14b

# Or with specific quantization
ollama pull lubtfy/csdl-14b:q4_k_m
```

### Step 4: Test

```bash
ollama run csdl-14b "Define a CSDL function to validate email"
```

## Manual Installation

If you want to install from the GGUF files directly:

### Step 1: Download Model Files

```bash
# Clone the repository (with Git LFS)
git lfs install
git clone https://github.com/LUBTFY/csdl-14b.git
cd csdl-14b

# Or download just the GGUF file
wget https://github.com/LUBTFY/csdl-14b/releases/download/v1.0/csdl-14b-q4_k_m.gguf
```

### Step 2: Create Ollama Model

```bash
# Navigate to the directory with the GGUF file
cd csdl-14b

# Create the model using the Modelfile
ollama create csdl-14b -f modelfiles/Modelfile
```

### Step 3: Verify Installation

```bash
# List models
ollama list

# Should show:
# NAME              ID            SIZE    MODIFIED
# csdl-14b:latest   abc123...     8.4 GB  Just now
```

## Installing LoRA Adapters

The specialized agents (Atlas, Marketing, NEXUS) use LoRA adapters on top of the base model.

### Step 1: Download Adapters

```bash
# Download from releases
wget https://github.com/LUBTFY/csdl-14b/releases/download/v1.0/atlas_lora.zip
wget https://github.com/LUBTFY/csdl-14b/releases/download/v1.0/marketing_lora.zip
wget https://github.com/LUBTFY/csdl-14b/releases/download/v1.0/nexus_lora.zip

# Extract
unzip atlas_lora.zip
unzip marketing_lora.zip
unzip nexus_lora.zip
```

### Step 2: Create Specialized Models

```bash
# Atlas - Reasoning specialist
ollama create csdl-14b-atlas -f modelfiles/Modelfile.atlas

# Marketing - Content specialist
ollama create csdl-14b-marketing -f modelfiles/Modelfile.marketing

# NEXUS - Code specialist
ollama create csdl-14b-nexus -f modelfiles/Modelfile.nexus
```

### Step 3: Verify All Models

```bash
ollama list

# Should show:
# NAME                    ID            SIZE    MODIFIED
# csdl-14b:latest         abc123...     8.4 GB  5 min ago
# csdl-14b-atlas:latest   def456...     8.5 GB  2 min ago
# csdl-14b-marketing:latest ghi789...   8.5 GB  1 min ago
# csdl-14b-nexus:latest   jkl012...     8.5 GB  Just now
```

## Verification

### Test Base Model

```bash
ollama run csdl-14b "Create a CSDL function definition for user authentication"
```

Expected output (JSON):
```json
{
  "t": "function",
  "n": "authenticate_user",
  "d": "Authenticate a user with credentials",
  "p": {
    "username": {"t": "string", "r": true},
    "password": {"t": "string", "r": true}
  },
  "r": {"t": "object", "p": ["token", "expires_at"]}
}
```

### Test Atlas (Reasoning)

```bash
ollama run csdl-14b-atlas "Plan a task to migrate a database to a new server"
```

### Test NEXUS (Coding)

```bash
ollama run csdl-14b-nexus "Generate a class for managing API rate limiting"
```

### Test API Access

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "csdl-14b",
  "prompt": "Define a function to search documents",
  "stream": false
}'
```

## Troubleshooting

### Model Not Found

```
Error: model 'csdl-14b' not found
```

**Solution**: Ensure you've created the model:
```bash
ollama create csdl-14b -f Modelfile
```

### Out of Memory

```
Error: out of memory
```

**Solutions**:
1. Close other applications to free RAM
2. Use a smaller quantization (Q4_K_S instead of Q4_K_M)
3. Reduce context length in the Modelfile:
   ```
   PARAMETER num_ctx 2048
   ```

### Slow Generation

**Solutions**:
1. Ensure Ollama is using GPU:
   ```bash
   ollama ps  # Check if GPU is being used
   ```
2. Reduce batch size
3. Use smaller context window

### Connection Refused

```
Error: connect ECONNREFUSED 127.0.0.1:11434
```

**Solution**: Start Ollama server:
```bash
ollama serve
```

### GGUF File Corrupted

```
Error: invalid gguf file
```

**Solution**: Re-download the file and verify checksum:
```bash
sha256sum csdl-14b-q4_k_m.gguf
# Compare with published checksum
```

## Uninstallation

To remove the models:

```bash
# Remove individual models
ollama rm csdl-14b
ollama rm csdl-14b-atlas
ollama rm csdl-14b-marketing
ollama rm csdl-14b-nexus

# Remove downloaded files
rm -rf csdl-14b/
```

---

For additional help, please [open an issue](https://github.com/LUBTFY/csdl-14b/issues).
