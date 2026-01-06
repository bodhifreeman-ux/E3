# CSDL Server

Python-based CSDL-14B inference server for DGX Spark with proper tokenization.

ANLT (Agent-Native Language Toolkit) provides the translation layer between human language and CSDL compressed format.

## Contents

- `csdl-venv/` - Python virtual environment with ANLT library
- `csdl-server.py` - CSDL inference server (FastAPI)

## Usage

### After PyTorch CUDA Build

1. Activate the PyTorch environment:
```bash
source /home/bodhifreeman/pytorch-build/pytorch-venv/bin/activate
```

2. Install dependencies:
```bash
pip install transformers accelerate fastapi uvicorn
```

3. Update `csdl-server.py` to use GPU:
```python
device_map="cuda:0"
torch_dtype=torch.bfloat16
```

4. Start the server:
```bash
cd /home/bodhifreeman/E3/E3/CSDL-ANLT
python3 csdl-server.py
```

5. Server runs on: `http://localhost:8003`

## Testing

```bash
curl -s http://localhost:8003/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [
      {"role": "system", "content": "You are CSDL-14B. Compress to CSDL Structured format."},
      {"role": "user", "content": "Compress: Build a JWT authentication system"}
    ],
    "max_tokens": 150
  }'
```

Expected output:
```json
{"T": "auth", "C": [{"id": "jwt"}], "cx": 0.8}
```

## Why This Exists

llama.cpp has a tokenization bug on ARM64 + Blackwell. This Python server uses HuggingFace Transformers for proper tokenization.

See [CSDL-14B/docs/CSDL-MODEL-DIAGNOSTIC.md](../CSDL-14B/docs/CSDL-MODEL-DIAGNOSTIC.md) for full investigation details.
