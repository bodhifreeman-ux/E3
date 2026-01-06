# CSDL-14B Setup Guide for DGX Spark

```
 ██████╗███████╗██████╗ ██╗          ███████╗██████╗  █████╗ ██████╗ ██╗  ██╗
██╔════╝██╔════╝██╔══██╗██║          ██╔════╝██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝
██║     ███████╗██║  ██║██║          ███████╗██████╔╝███████║██████╔╝█████╔╝
██║     ╚════██║██║  ██║██║          ╚════██║██╔═══╝ ██╔══██║██╔══██╗██╔═██╗
╚██████╗███████║██████╔╝███████╗     ███████║██║     ██║  ██║██║  ██║██║  ██╗
 ╚═════╝╚══════╝╚═════╝ ╚══════╝     ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
```

**Complete Setup Guide for CSDL-14B on NVIDIA DGX Spark**
**Version 1.0** | January 2026

---

## Overview

This document provides everything needed to run CSDL-14B (our fine-tuned Qwen2.5-14B compression model) on the DGX Spark. The model performs bidirectional compression between human language and CSDL (Compressed Semantic Data Language) format.

**If you're getting garbage/Chinese characters:** The issue is almost certainly the chat template or tokenizer configuration.

---

## Architecture on Geekom (Reference)

The Geekom uses a **hybrid setup**:

| Port | Service | Model | Purpose |
|------|---------|-------|---------|
| 8080 | llama-server | CSDL-14B (via Ollama blob) | Compression + Reasoning |
| 11434 | Ollama | Various Qwen models | Content + Coding tasks |

**Key insight:** llama-server on port 8080 runs the CSDL-14B model that Ollama manages. The model file is stored by Ollama at:
```
/usr/share/ollama/.ollama/models/blobs/sha256-aa9687722deee23a9488008f2d8652eba887031cf25f928c38772f72cfa4c7d9
```

This is the CSDL-14B model registered with Ollama (`ollama create csdl-14b`) then loaded directly by llama-server for the OpenAI-compatible API.

**IMPORTANT:** When using llama-server directly (not via Ollama), the model name in API calls must match the filename or hash. The backend code uses `"model": "csdl-14b"` but llama-server may report the model as its hash. Either works if configured correctly.

### Verified Working Test (Geekom, January 2026)
```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a CSDL translator. Convert human language to minimal JSON.\nUse abbreviated keys: T=type, src=source, q=query, n=name, s=steps, a=args\nOutput ONLY valid JSON."},
      {"role": "user", "content": "Search the knowledge base for customer billing procedures and return the top 5 results."}
    ],
    "max_tokens": 200,
    "temperature": 0.1
  }'

# OUTPUT: {"T":"search","src":"kb","q":"billing","lim":5}
```

### .env Configuration (Geekom)
```bash
# llama-server on port 8080 (CSDL-14B)
OLLAMA_BASE_URL=http://localhost:8080
OLLAMA_MODEL=csdl-14b
CSDL_14B_SERVER_URL=http://localhost:8080

# Tiered models (can use Ollama on 11434 or separate llama-server instances)
LLAMA_CSDL_URL=http://localhost:8080/v1      # CSDL-14B
LLAMA_CONTENT_URL=http://localhost:8081/v1   # qwen-7b (optional)
LLAMA_CODER_URL=http://localhost:8082/v1     # qwen-coder-14b (optional)
```

---

## 1. Required Files from Geekom

Copy these directories/files from the external drive or Geekom machine:

### Model Files
```
/home/christian/csdl-model/
├── csdl-14b-q4_k_m.gguf      # 8.4GB - Quantized model (recommended)
├── merged_16bit/              # Full F16 weights (if you want F16)
│   └── [safetensors files]
└── Modelfile                  # Ollama config (reference only)
```

### ANLT Translation Layer (CRITICAL)
```
/home/christian/csdl-agency/csdl-anlt/
├── src/
│   └── anlt/
│       ├── __init__.py
│       ├── translator.py      # Core ANLT v1 translator
│       ├── vocabulary.py      # Compression vocabulary
│       ├── token_counter.py   # Token counting
│       ├── csdl_structured.py # Structured CSDL format
│       └── v2/
│           └── enhanced.py    # V2 enhanced compressor
├── requirements.txt
└── setup.py
```

### Backend Integration (Optional - for full platform)
```
/home/christian/csdl-agency/CSDL-Agent-UI/platform/backend/app/core/anlt.py
/home/christian/csdl-agency/CSDL-Agent-UI/platform/backend/app/integrations/csdl_pipeline.py
```

---

## 2. llama.cpp Server Setup

### Install llama.cpp (if not already)
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
mkdir build && cd build
cmake .. -DGGML_CUDA=ON
cmake --build . --config Release -j$(nproc)
```

### Start llama-server with CSDL-14B

**For Q4_K_M quantized (recommended for testing):**
```bash
./llama-server \
    --model /path/to/csdl-14b-q4_k_m.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    --ctx-size 8192 \
    --parallel 2 \
    --n-gpu-layers 99 \
    --chat-template chatml
```

**For F16 (full precision):**
```bash
./llama-server \
    --model /path/to/csdl-14b-f16.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    --ctx-size 8192 \
    --parallel 2 \
    --n-gpu-layers 99 \
    --chat-template chatml
```

### Critical Flags

| Flag | Purpose |
|------|---------|
| `--chat-template chatml` | **CRITICAL** - Qwen2.5 uses ChatML format |
| `--ctx-size 8192` | Context window size |
| `--n-gpu-layers 99` | Offload all layers to GPU |
| `--parallel 2` | Concurrent request handling |

---

## 3. Chat Template (CRITICAL)

CSDL-14B is fine-tuned from Qwen2.5-14B which uses the **ChatML** template:

```
<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
{assistant_response}<|im_end|>
```

**If you see garbage/Chinese characters, the template is wrong.**

### Verify Template is Working
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Say hello"}
    ],
    "max_tokens": 50,
    "temperature": 0.1
  }'
```

Expected: Clean English response like "Hello! How can I help you today?"

---

## 4. CSDL Compression Test

### System Prompt for CSDL Compression
```
You are a CSDL translator. Convert human language to minimal JSON.
Use abbreviated keys: T=type, src=source, q=query, n=name, s=steps, a=args
Use abbreviated values: kb=knowledge_base, auth=authentication, mem=memory
Output ONLY valid JSON, nothing else.
```

### Test Compression
```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [
      {"role": "system", "content": "You are a CSDL translator. Convert human language to minimal JSON.\nUse abbreviated keys: T=type, src=source, q=query, n=name, s=steps, a=args\nUse abbreviated values: kb=knowledge_base, auth=authentication, mem=memory\nOutput ONLY valid JSON, nothing else."},
      {"role": "user", "content": "Search the knowledge base for information about customer billing procedures and return the top 5 results."}
    ],
    "max_tokens": 200,
    "temperature": 0.1
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['choices'][0]['message']['content'])"
```

### Expected Output (example)
```json
{"T":"search","src":"kb","q":"customer billing procedures","n":5}
```

### Test Expansion (CSDL -> Human)
```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [
      {"role": "system", "content": "You are a CSDL translator. Expand CSDL JSON to clear, natural human language. Be concise but informative. Output ONLY the human-readable text."},
      {"role": "user", "content": "{\"T\":\"search\",\"src\":\"kb\",\"q\":\"billing\",\"n\":5}"}
    ],
    "max_tokens": 200,
    "temperature": 0.1
  }' | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['choices'][0]['message']['content'])"
```

### Expected Output
```
Search the knowledge base for information about billing and return the top 5 results.
```

---

## 5. Install ANLT Package

The ANLT (Agent-Native Language Translation) package provides the v1 and v2 compression layers. **This is NOT on the Spark yet - you need to copy it from Geekom or the external drive.**

### Option A: Copy from Geekom/External Drive
```bash
# From Geekom
scp -r /home/christian/csdl-agency/csdl-anlt dgx-spark:/opt/

# Or from external drive (if already copied there)
cp -r /media/external/csdl-anlt /opt/
```

### Option B: Create from source files

If you can't copy the directory, here are the essential files. Create this structure on the Spark:

```
/opt/csdl-anlt/
├── setup.py
├── requirements.txt
└── src/
    └── anlt/
        ├── __init__.py
        ├── translator.py
        ├── vocabulary.py
        ├── token_counter.py
        ├── csdl_structured.py
        └── v2/
            ├── __init__.py
            └── enhanced.py
```

### setup.py
```python
from setuptools import setup, find_packages

setup(
    name="anlt",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tiktoken>=0.5.0",
    ],
    python_requires=">=3.10",
)
```

### requirements.txt
```
tiktoken>=0.5.0
```

### Install the package
```bash
cd /opt/csdl-anlt
pip install -e .
```

### Test ANLT Installation
```python
from anlt import ANLT
from anlt.v2 import EnhancedCompressor
from anlt.token_counter import TokenCounter

# V1 Translation
anlt = ANLT()
compressed = anlt.translate_to_agent("Search for customer billing information")
print(f"V1: {compressed}")

# V2 Enhanced
v2 = EnhancedCompressor()
compressed_v2 = v2.compress_enhanced("Search for customer billing information")
print(f"V2: {compressed_v2}")

# Token counting
counter = TokenCounter()
tokens = counter.count_text("Search for customer billing information")
print(f"Tokens: {tokens}")
```

### If you need the actual source files

The key files from Geekom are:

**src/anlt/__init__.py:**
```python
from .translator import ANLT
from .vocabulary import CSDLVocabulary
from .token_counter import TokenCounter

__all__ = ['ANLT', 'CSDLVocabulary', 'TokenCounter']
```

**src/anlt/v2/__init__.py:**
```python
from .enhanced import EnhancedCompressor

__all__ = ['EnhancedCompressor']
```

For the full source code of `translator.py`, `vocabulary.py`, `token_counter.py`, and `v2/enhanced.py`, you'll need to copy them from:
- `/home/christian/csdl-agency/csdl-anlt/src/anlt/` on Geekom
- Or the external drive if you've copied the repo there

---

## 6. Compression Levels (Multi-Layer Architecture)

The CSDL system uses **layered compression** where each level builds on the previous:

| Level | Reduction | Method | Requirements |
|-------|-----------|--------|--------------|
| v1 | ~35% | Key abbreviation (JSON keys → short form) | ANLT package only |
| v2_enhanced | ~42% avg | Vocabulary-based (common terms → codes) | ANLT package only |
| v2_semantic | **55.4% verified** | CSDL-14B model (semantic compression) | llama-server + CSDL-14B |
| v2_semantic_full | 70-90% | Embedding compression | + sentence-transformers |
| **CBP Binary** | **85-98%** | MessagePack + dedup + delta | msgpack, xxhash, lz4 |

### How the Layers Stack

```
Human Text (100 tokens)
    ↓ V1: Key abbreviation
Abbreviated JSON (~65 tokens, 35% reduction)
    ↓ V2: Vocabulary encoding
Encoded Format (~58 tokens, 42% total reduction)
    ↓ V2 Semantic: CSDL-14B model
Semantic CSDL (~45 tokens, 55.4% verified reduction)
    ↓ V2 Semantic Full: + Embeddings
Embedding Vector (~5 tokens, 90%+ reduction)
```

### CBP Binary Protocol (85-98% Reduction)

**CBP (CSDL Binary Protocol)** is the highest compression layer - world's first binary protocol for LLM agents.

**Source files included in this bundle:**
- `09_CBP_Protocol_Source.py` - Core encoder/decoder/delta
- `10_CBP_Schema_Source.py` - Schema definitions
- `11_Semantic_Compressor_Source.py` - Embedding compression

**Dependencies:**
```bash
pip install msgpack xxhash lz4 sentence-transformers
```

**What CBP does:**
1. **MessagePack** - Binary instead of JSON text
2. **Numeric Field IDs** - 1 byte instead of string keys ("content" → 0x04)
3. **Semantic Deduplication** - Same content = 8-byte hash reference
4. **Delta Encoding** - Only transmit changes between messages
5. **LZ4 Compression** - Optional for large payloads

**Usage:**
```python
from cbp_protocol import encode_message, decode_message

# Encode
message = {"type": "handoff", "sender": "Analyzer", "receiver": "Strategist", "content": {...}}
cbp_bytes, metrics = encode_message(message)
print(f"Reduction: {metrics.reduction_percent}%")

# Decode
decoded_msg, decode_metrics = decode_message(cbp_bytes)
```

**Full documentation:** See `08_CSDL_Compression_Full_Stack.md`

### Verified Compression Rate (55.4%)

The **55.4% verified** rate comes from CSDL-14B v2_semantic level, tested January 2026 with diverse prompts. This is the primary compression method used for agent-to-agent communication in the ATLAS reasoning system.

---

## 7. Troubleshooting

### Problem: Garbage/Chinese Characters Output

**Cause:** Wrong chat template or tokenizer issue.

**Solutions:**
1. Add `--chat-template chatml` flag to llama-server
2. If using GGUF converted from safetensors, ensure tokenizer.json was included
3. Try the native `/completion` endpoint with manual template:

```bash
curl http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\nSay hello<|im_end|>\n<|im_start|>assistant\n",
    "n_predict": 50,
    "temperature": 0.1,
    "stop": ["<|im_end|>"]
  }'
```

### Problem: Model Not Loading

**Check:**
```bash
# Verify GGUF file integrity
sha256sum /path/to/model.gguf

# Check GPU memory
nvidia-smi

# Check llama-server logs
./llama-server --model /path/to/model.gguf --verbose
```

### Problem: Slow Inference

**For DGX Spark with Grace CPU + Blackwell GPU:**
```bash
./llama-server \
    --model /path/to/csdl-14b-f16.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    --ctx-size 8192 \
    --parallel 4 \
    --n-gpu-layers 99 \
    --flash-attn \
    --chat-template chatml
```

### Problem: ANLT Import Error

```bash
# Ensure ANLT is installed
pip show anlt

# If not found, install from source
cd /path/to/csdl-anlt
pip install -e .
```

---

## 8. Health Check Endpoints

### llama-server Health
```bash
curl http://localhost:8080/health
# Expected: {"status":"ok"}
```

### Model Info
```bash
curl http://localhost:8080/v1/models
```

### Props (detailed info)
```bash
curl http://localhost:8080/props
```

---

## 9. Python Integration Example

```python
import httpx
import json

class CSDL14BCompressor:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url

    async def compress(self, text: str) -> str:
        """Compress human text to CSDL format"""
        system_prompt = """You are a CSDL translator. Convert human language to minimal JSON.
Use abbreviated keys: T=type, src=source, q=query, n=name, s=steps, a=args
Use abbreviated values: kb=knowledge_base, auth=authentication, mem=memory
Output ONLY valid JSON, nothing else."""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": "csdl-14b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.1
                }
            )
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def expand(self, csdl_json: str) -> str:
        """Expand CSDL format back to human text"""
        system_prompt = """You are a CSDL translator. Expand CSDL JSON to clear, natural human language.
Be concise but informative. Output ONLY the human-readable text."""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": "csdl-14b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": csdl_json}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.1
                }
            )
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

# Usage
import asyncio

async def main():
    compressor = CSDL14BCompressor()

    # Compress
    text = "Search the knowledge base for customer billing procedures"
    compressed = await compressor.compress(text)
    print(f"Compressed: {compressed}")

    # Expand
    expanded = await compressor.expand(compressed)
    print(f"Expanded: {expanded}")

asyncio.run(main())
```

---

## 10. Reference: Geekom Setup

### llama.cpp Version on Geekom
```
version: 7551 (a52dc60ba)
built with GNU 13.3.0 for Linux x86_64
```

### Geekom Start Command (from startup script)
```bash
HSA_OVERRIDE_GFX_VERSION=11.0.0 /home/christian/llama.cpp/build/bin/llama-server \
    --model /home/christian/csdl-agency/models/csdl-14b-q8_0.gguf \
    --host 0.0.0.0 --port 8080 \
    --ctx-size 8192 --parallel 2 \
    --n-gpu-layers 99
```

Note: `HSA_OVERRIDE_GFX_VERSION=11.0.0` is AMD ROCm specific - not needed on NVIDIA.

---

## 11. Files to Copy Summary

```
FROM EXTERNAL DRIVE/GEEKOM:
├── csdl-model/
│   ├── csdl-14b-q4_k_m.gguf     # Or F16 version
│   └── merged_16bit/            # If using F16
│
├── csdl-anlt/                   # ENTIRE DIRECTORY
│   ├── src/anlt/
│   ├── requirements.txt
│   └── setup.py
│
└── (Optional) CSDL-Agent-UI/platform/backend/app/
    ├── core/anlt.py
    └── integrations/csdl_pipeline.py
```

---

## Quick Start Checklist

- [ ] Copy model file (GGUF) to DGX Spark
- [ ] Copy and install csdl-anlt package (`pip install -e .`)
- [ ] Build llama.cpp with CUDA support
- [ ] Start llama-server with `--chat-template chatml`
- [ ] Test health endpoint: `curl http://localhost:8080/health`
- [ ] Test simple chat completion (should return English)
- [ ] Test CSDL compression (should return JSON)
- [ ] Test CSDL expansion (should return human text)

---

## 12. Installing CSDL Agent UI on DGX Spark

If you want the full platform UI (not just CSDL compression), here's what you need:

### Repositories Required

| Repository | Purpose | Required? |
|------------|---------|-----------|
| `csdl-agency/CSDL-Agent-UI/` | Main platform (backend + frontend) | **Yes** |
| `csdl-agency/csdl-anlt/` | ANLT compression library | **Yes** |
| `csdl-model/` | CSDL-14B model files | **Yes** |
| `csdl-agency/Archon/` | Knowledge base system | Optional |
| `csdl-agency/CSDL-Agent-Chat-Widget/` | Embeddable chat widget | Optional |

### Option A: Clone the entire csdl-agency repo

This is the simplest approach - gives Claude Code access to everything:

```bash
# On DGX Spark
git clone <your-git-remote> csdl-agency
cd csdl-agency
```

The repo structure:
```
csdl-agency/
├── CSDL-Agent-UI/
│   └── platform/
│       ├── backend/          # FastAPI backend (Python 3.11+)
│       ├── frontend/         # Next.js frontend
│       └── .env              # Environment config
├── csdl-anlt/                # ANLT package
├── Archon/                   # Knowledge base (Docker)
├── CSDL-Agent-Chat-Widget/   # Widget for client sites
├── csdl-14b/                 # Model training files
└── docs/                     # Documentation
```

### Option B: Selective copy

If you only want the UI platform:

```bash
# Copy these from Geekom/external drive:
scp -r /home/christian/csdl-agency/CSDL-Agent-UI dgx-spark:/opt/
scp -r /home/christian/csdl-agency/csdl-anlt dgx-spark:/opt/
scp -r /home/christian/csdl-model dgx-spark:/opt/
```

### Backend Setup (FastAPI)

```bash
cd CSDL-Agent-UI/platform/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install ANLT package
pip install -e /path/to/csdl-anlt

# Copy and configure .env
cp .env.example .env
# Edit .env with correct paths and URLs
```

### Key .env Configuration for DGX Spark

```bash
# Database (PostgreSQL required)
DATABASE_URL=postgresql://user:pass@localhost:5432/csdl_agent

# Redis (required for caching)
REDIS_URL=redis://localhost:6379/0

# CSDL-14B via llama-server
OLLAMA_BASE_URL=http://localhost:8080
CSDL_14B_SERVER_URL=http://localhost:8080
USE_CSDL_14B_FOR_COMPRESSION=true

# Qdrant for vector storage
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Data directory (for infinite memory SQLite)
DATA_DIR=./data
```

### Frontend Setup (Next.js)

```bash
cd CSDL-Agent-UI/platform/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Or run in dev mode
npm run dev
```

### Required Services

| Service | Port | How to Start |
|---------|------|--------------|
| PostgreSQL | 5432 | `docker run -d -p 5432:5432 postgres:15` |
| Redis | 6379 | `docker run -d -p 6379:6379 redis:7` |
| Qdrant | 6333 | `docker run -d -p 6333:6333 qdrant/qdrant` |
| llama-server | 8080 | See Section 2 |
| Backend | 8000 | `uvicorn app.main:app --port 8000` |
| Frontend | 3000 | `npm run dev` |

### Start Script for DGX Spark

Create `/opt/start-csdl-ui.sh`:

```bash
#!/bin/bash
# CSDL Agent UI - DGX Spark Start Script

# Start llama-server (CSDL-14B)
nohup /path/to/llama-server \
    --model /path/to/csdl-14b.gguf \
    --host 0.0.0.0 --port 8080 \
    --ctx-size 8192 --parallel 4 \
    --n-gpu-layers 99 \
    --chat-template chatml \
    > /var/log/llama-server.log 2>&1 &

# Wait for model to load
sleep 10

# Start backend
cd /opt/CSDL-Agent-UI/platform/backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 \
    > /var/log/csdl-backend.log 2>&1 &

# Start frontend
cd /opt/CSDL-Agent-UI/platform/frontend
nohup npm run start \
    > /var/log/csdl-frontend.log 2>&1 &

echo "CSDL Agent UI started"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  llama-server: http://localhost:8080"
```

### Connecting Your 32 Multi-Agent System

If you already have 32 agents running on the Spark without UI, you can integrate them:

1. **Register agents with the backend:**
   - The backend's agent registry (`/app/core/agent_registry.py`) manages agents
   - POST to `/api/agents/register` with agent config

2. **Enable CSDL compression for agent-to-agent communication:**
   ```python
   from anlt import ANLT
   from anlt.v2 import EnhancedCompressor

   # In your agent communication layer
   anlt = ANLT()
   message_compressed = anlt.translate_to_agent(message)
   # Send compressed message between agents
   ```

3. **Use the CSDL-14B model for semantic compression:**
   ```python
   # Call llama-server for v2_semantic compression
   response = httpx.post("http://localhost:8080/v1/chat/completions", json={
       "messages": [
           {"role": "system", "content": "You are a CSDL translator..."},
           {"role": "user", "content": agent_message}
       ]
   })
   ```

---

## 13. What Claude Code Needs Access To

For Claude Code on the DGX Spark to have full context, **prioritize README files in each directory** - they contain the most accurate and up-to-date technical information.

### CRITICAL - README Files (Read These First)

Each README.md contains authoritative documentation for that component:

```
csdl-agency/
├── README.md                                    # Root - LUBTFY overview, pricing, services
├── CLAUDE.md                                    # Project context (critical paths)
│
├── CSDL-Agent-UI/
│   ├── README.md                                # Platform overview, architecture, features
│   └── platform/
│       └── README.md                            # Detailed setup: backend, frontend, APIs
│
├── csdl-anlt/
│   └── README.md                                # CSDL dual-format compression (64-90%)
│                                                # - CSDL Structured: agent reasoning
│                                                # - CSDL Embedding: max compression
│                                                # - Web dashboard, REST API
│
├── csdl-14b/
│   └── README.md                                # CSDL-14B model (98% compression)
│                                                # - CBP binary protocol
│                                                # - Schema registry
│                                                # - Semantic deduplication
│                                                # - Delta encoding
│
├── CSDL-Agent-Chat-Widget/
│   └── README.md                                # Embeddable chat widget
│                                                # - Glassmorphism design
│                                                # - WebSocket messaging
│                                                # - Client configuration
│
├── Archon/
│   └── README.md                                # Knowledge base MCP server
│                                                # - Web crawling
│                                                # - Document processing
│                                                # - RAG strategies
│                                                # - Task management
│
└── self-discovery-agent/
    └── README.md                                # Wisdom agent example
```

### README Content Summary

| README | Key Topics | Priority |
|--------|-----------|----------|
| **csdl-agency/README.md** | Services, pricing, tech overview, repo structure | Context |
| **CSDL-Agent-UI/README.md** | CSDL/ANLT concepts, Atlas multi-agent, features, architecture | **Critical** |
| **csdl-anlt/README.md** | Dual-format compression, structured vs embedding, API, ROI | **Critical** |
| **csdl-14b/README.md** | CBP protocol, schema registry, dedup, delta encoding, 98% compression | **Critical** |
| **Chat-Widget/README.md** | Widget features, configuration, deployment | High |
| **Archon/README.md** | MCP server, RAG, web crawling, services | High |
| **self-discovery-agent/README.md** | Agent example, integration pattern | Medium |

### CRITICAL - Source Code Access
```
csdl-anlt/src/anlt/                              # ANLT library source
├── __init__.py
├── translator.py                                # Core v1 translator
├── vocabulary.py                                # Compression vocabulary
├── token_counter.py                             # Token counting
├── csdl_structured.py                           # Structured format
└── v2/
    └── enhanced.py                              # V2 enhanced compressor
```

### HIGH PRIORITY - Technical Docs (Supplement READMEs)
```
docs/NEW/
├── 00_Platform_Overview.md                      # Full system architecture
├── 02_CSDL_Technology.md                        # CSDL compression deep-dive
├── 03_ANLT_Translation.md                       # ANLT layer details
├── 07_Technical_Specifications.md               # All specs and metrics
└── features/
    ├── CSDL_Messaging.md                        # CSDL protocol details
    ├── Atlas_Reasoning.md                       # Multi-agent reasoning
    └── Cognitive_Tiers.md                       # Model tier system
```

### MEDIUM PRIORITY - Additional Technical Docs
```
docs/NEW/
├── Technical_Systems_Overview.md                # System components
├── Infinite_Memory_System.md                    # Memory architecture
├── CSDL_Federation_Architecture.md              # Federation design
├── 08_Testing_Guide.md                          # Testing procedures
└── plans/
    ├── Atlas_Nexus_Pipeline.md                  # ATLAS + NEXUS integration
    └── DGX_Spark_Finetuning.md                  # Finetuning on Spark
```

### LOW PRIORITY - Skip for Technical Setup
```
docs/NEW/
├── Client_*.md                                  # Client-facing docs (sales)
├── Sales_*.md                                   # Sales materials
├── Investor_*.md                                # Investor docs
├── LinkedIn_*.md                                # Marketing
└── sales_docs/                                  # Sales collateral
```

### Source Code Reference
```
CSDL-Agent-UI/platform/
├── backend/
│   └── app/
│       ├── main.py                              # FastAPI entry point
│       ├── core/
│       │   ├── anlt.py                          # ANLT integration
│       │   ├── config.py                        # Configuration
│       │   ├── agent_registry.py                # Agent management
│       │   └── csdl_messaging.py                # CSDL protocol
│       ├── services/
│       │   ├── infinite_memory_service.py       # Memory system
│       │   └── llm_service.py                   # LLM abstraction
│       └── integrations/
│           └── csdl_pipeline.py                 # Full CSDL pipeline
└── frontend/                                    # Next.js UI
```

---

## 14. Recommended Reading Order for Claude Code

When Claude Code on DGX Spark starts, it should read **README files first** as they contain the most accurate technical information:

### Phase 1: Core Understanding (Start Here)
1. **CLAUDE.md** - Project context and critical paths
2. **This document** (DGX_Spark_CSDL_Setup.md) - Spark-specific setup
3. **csdl-agency/README.md** - Overall project structure and services

### Phase 2: Core Technology READMEs
4. **CSDL-Agent-UI/README.md** - Main platform architecture
5. **csdl-anlt/README.md** - CSDL dual-format compression system
6. **csdl-14b/README.md** - CSDL-14B model and CBP protocol

### Phase 3: Component READMEs
7. **CSDL-Agent-Chat-Widget/README.md** - Widget implementation
8. **Archon/README.md** - Knowledge base MCP server
9. **self-discovery-agent/README.md** - Agent implementation example

### Phase 4: Source Code
10. **csdl-anlt/src/anlt/** - ANLT library source code
11. **DGX_Spark_ANLT_Source.md** - Full ANLT source (if csdl-anlt not copied)

### Phase 5: Supplementary Docs (If Needed)
12. **docs/NEW/02_CSDL_Technology.md** - Additional CSDL details
13. **docs/NEW/features/CSDL_Messaging.md** - Protocol implementation

---

## 15. Quick Copy Commands

### Copy everything (recommended):
```bash
# From Geekom to DGX Spark
rsync -avz /home/christian/csdl-agency/ dgx-spark:/opt/csdl-agency/

# Or via external drive
cp -r /home/christian/csdl-agency /media/external/
# Then on Spark:
cp -r /media/external/csdl-agency /opt/
```

### Copy README files bundle (Quick reference for Claude Code):

All README files have been copied to a single directory:
```
docs/README_files/
├── 00_ROOT_README.md           # csdl-agency/README.md
├── 01_CSDL_Agent_UI_README.md  # CSDL-Agent-UI/README.md
├── 02_CSDL_ANLT_README.md      # csdl-anlt/README.md
├── 03_CSDL_14B_README.md       # csdl-14b/README.md
├── 04_Chat_Widget_README.md    # CSDL-Agent-Chat-Widget/README.md
├── 05_Archon_README.md         # Archon/README.md
└── 06_Self_Discovery_Agent_README.md
```

```bash
# Copy just the README bundle
scp -r /home/christian/csdl-agency/docs/README_files dgx-spark:/opt/csdl-docs/
```

### Copy only essential docs:
```bash
# Create docs directory on Spark
ssh dgx-spark "mkdir -p /opt/csdl-docs"

# Copy critical files (READMEs + setup guides)
scp /home/christian/csdl-agency/CLAUDE.md dgx-spark:/opt/csdl-docs/
scp /home/christian/csdl-agency/docs/DGX_Spark_CSDL_Setup.md dgx-spark:/opt/csdl-docs/
scp /home/christian/csdl-agency/docs/DGX_Spark_ANLT_Source.md dgx-spark:/opt/csdl-docs/
scp -r /home/christian/csdl-agency/docs/README_files/ dgx-spark:/opt/csdl-docs/

# Copy ANLT library (required for installation)
scp -r /home/christian/csdl-agency/csdl-anlt/ dgx-spark:/opt/csdl-anlt/
```

### Copy for full platform installation:
```bash
# Essential for running CSDL Agent UI
scp -r /home/christian/csdl-agency/CSDL-Agent-UI dgx-spark:/opt/
scp -r /home/christian/csdl-agency/csdl-anlt dgx-spark:/opt/
scp -r /home/christian/csdl-model dgx-spark:/opt/

# Optional but useful
scp -r /home/christian/csdl-agency/Archon dgx-spark:/opt/
scp -r /home/christian/csdl-agency/docs dgx-spark:/opt/
scp /home/christian/csdl-agency/CLAUDE.md dgx-spark:/opt/
```

---

## 16. Document Count Summary

| Category | Count | Priority |
|----------|-------|----------|
| **README files** | **7** | **Critical** |
| Project guide (CLAUDE.md) | 1 | Critical |
| Setup docs (this + ANLT Source) | 2 | Critical |
| Core technical docs | 7 | High |
| ANLT source code files | 6 | High |
| Feature docs | 7 | Medium |
| Plans | 3 | Medium |
| Sales/Business docs | 15+ | Low (skip) |

**For DGX Spark setup, focus on:**
1. **7 README files** (all in `docs/README_files/`)
2. **CLAUDE.md** (project guide)
3. **This document** + **DGX_Spark_ANLT_Source.md**
4. **csdl-anlt/src/anlt/*** (6 source files)

Total essential files: ~17 documents

---

*Document prepared for DGX Spark deployment | January 2026*
