# CSDL-ANLT - Compressed Semantic Data Language Translation Layer

> Proprietary compression protocol for E3's 32-agent swarm communication

## Overview

CSDL-ANLT provides the translation and compression layer between:
- **Human language** (natural input/output at system edges)
- **CSDL format** (compressed semantic representation for inter-agent communication)

## Compression Layers

| Layer | Component | Compression | Description |
|-------|-----------|-------------|-------------|
| 1 | ANLT Translator | Semantic extraction | Natural language → CSDL field codes |
| 2 | Semantic Embeddings | 80-90% | Dense vector representations |
| 3 | CBP Binary | 30-60% | MessagePack + LZ4 wire format |
| 4 | Deduplication | 86%+ | xxHash content-addressed storage |

## CSDL Field Codes

Single-character keys for maximum compression:

| Code | Field | Values |
|------|-------|--------|
| `T` | Type | q=query, c=cmd, r=result, x=error, h=handoff |
| `C` | Content | `{i: intent, k: keywords}` |
| `R` | Response | b=brief, d=detailed, s=structured, a=action |
| `cx` | Context | Scope, domain, temporal markers |
| `p` | Priority | 0=low, 1=normal, 2=high, 3=critical |
| `m` | Metadata | Optional additional data |

**Intent Codes:**
- `an` = analyze, `rk` = risk, `ds` = design, `im` = implement
- `ts` = test, `op` = optimize, `sc` = security, `qr` = query

## Components

### csdl-server.py
CSDL-14B inference server using HuggingFace Transformers on GPU.

```bash
# Start server (requires PyTorch CUDA build)
source /home/bodhifreeman/pytorch-build/pytorch-venv/bin/activate
python csdl-server.py
# Server: http://localhost:5000
```

### src/cbp/
CBP (Compressed Binary Protocol) implementation:
- `cbp_protocol.py` - Encoder/decoder with deduplication
- `cbp_schema.py` - Field ID mappings for all 32 agents
- `semantic_compressor.py` - Embedding-based compression

### test_compression_layers.py
Comprehensive test suite for all 4 compression layers.

```bash
python test_compression_layers.py
```

## Verified Compression Results

```
Single message (CBP vs JSON):     ~30% reduction
Multi-hop pipeline (4 agents):    ~46% reduction
Repeated queries (10x same):      ~86% reduction
Dedup hit rate:                   90%+
```

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
# {"status": "ok", "model_loaded": true}
```

### Chat Completion (Ollama-compatible)
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [{"role": "user", "content": "What is CSDL?"}]
  }'
```

### OpenAI-compatible
```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "csdl-14b",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

## Why Not llama.cpp?

llama.cpp has a tokenization bug on ARM64 + Blackwell (compute capability 12.1) that produces gibberish output. The HuggingFace Transformers server uses proper tokenization.

See [CSDL-14B/docs/CSDL-MODEL-DIAGNOSTIC.md](../CSDL-14B/docs/CSDL-MODEL-DIAGNOSTIC.md) for investigation details.

## Requirements

- PyTorch 2.11+ built with CUDA 13.0 (for Blackwell)
- transformers, accelerate, fastapi, uvicorn
- msgpack, xxhash, lz4 (for CBP)
- sentence-transformers (for semantic embeddings)

## License

Proprietary - E3 Consortium
