# E3 - Emergent Engineering Environment

> AI-powered development platform with 32-agent swarm, local LLM inference, and proprietary CSDL compression protocol

## Current Status

| Component | Status | Port | Description |
|-----------|--------|------|-------------|
| **CSDL-14B Server** | ✅ Running | 5000 | HuggingFace Transformers on GPU |
| **AG-UI Server** | ✅ Running | 8100 | Agent-UI Protocol Server |
| **DevMind UI** | ✅ Running | 3000 | CopilotKit React Frontend |
| **Archon RAG** | ✅ Running | 8181, 8051, 3737 | RAG System |

**Hardware**: NVIDIA DGX Spark (Grace Blackwell GB10, 128GB unified memory, CUDA 13.0)
**PyTorch**: Built from source with CUDA 13.0 support for Blackwell architecture

## Quick Start

### Start Full Stack
```bash
# Option 1: Desktop launcher
# Click "Start E3 Full Stack" on desktop

# Option 2: Command line
./Scripts/start-e3-full-stack.sh
```

### Start DevMind Swarm Only
```bash
# Requires CSDL and Archon running first
./Scripts/start-e3-devmind-swarm.sh
```

### Access Points
- **DevMind UI**: http://localhost:3000
- **AG-UI Server**: http://localhost:8100
- **CSDL API**: http://localhost:5000
- **Archon UI**: http://localhost:3737

## Architecture

```
+====================================================================================+
|                              E3 DEVMIND PLATFORM                                   |
+====================================================================================+
|                                                                                    |
|    +------------------+      +------------------+      +------------------+        |
|    |   CopilotKit     |      |     AG-UI        |      |    32-Agent      |        |
|    |    React UI      |<---->|     Server       |<---->|     Swarm        |        |
|    |   (Port 3000)    |      |   (Port 8100)    |      |   (LangGraph)    |        |
|    +------------------+      +------------------+      +------------------+        |
|                                      |                         |                   |
|                                      v                         v                   |
|    +-------------------------------------+   +-------------------------------------+
|    |         CSDL-14B SERVER             |   |        ARCHON RAG SYSTEM           |
|    |           (Port 5000)               |   |   API:8181 | MCP:8051 | UI:3737    |
|    |      Ollama-Compatible API          |   +-------------------------------------+
|    |      NVIDIA DGX Spark 128GB         |                                        |
|    +-------------------------------------+                                        |
+====================================================================================+
```

## Components

### CSDL-14B - Local LLM
- **Base**: Qwen2.5-14B-Instruct (14.7B parameters)
- **Training**: 32,000+ CSDL compression examples
- **Inference**: HuggingFace Transformers + PyTorch CUDA (NOT llama.cpp - tokenization bug on ARM64+Blackwell)
- **Hardware**: NVIDIA DGX Spark (Grace Blackwell GB10, 128GB unified memory)
- **Format**: bfloat16 on GPU

### E3-DevMind-AI - 32-Agent Swarm
- **32 specialized agents** in 7-tier hierarchy
- **LangGraph** orchestration
- **AG-UI Protocol** for streaming
- **CopilotKit** React frontend

### CSDL Compression Protocol (Proprietary)

The **Compressed Semantic Data Language (CSDL)** protocol is the core of E3's efficiency. It provides 4 layers of compression:

| Layer | Technology | Compression | Use Case |
|-------|------------|-------------|----------|
| **Layer 1** | ANLT Translation | Semantic extraction | Human ↔ CSDL at edges |
| **Layer 2** | Semantic Embeddings | 80-90% | Dense vector similarity |
| **Layer 3** | CBP Binary (MessagePack+LZ4) | 30-60% | Wire protocol |
| **Layer 4** | Deduplication (xxHash) | **86%+** | Repeated content in pipelines |

**CSDL Field Codes:**
- `T`: Type (q=query, c=cmd, r=result, x=error)
- `C`: Content (semantic payload with `i`=intent, `k`=keywords)
- `R`: Response format (b=brief, d=detailed, s=structured)
- `cx`: Context (scope, domain, temporal)
- `p`: Priority (0-3)

**Compression Results (Verified):**
```
Single message (CBP vs JSON):     ~30% reduction
Multi-hop pipeline (4 agents):    ~46% reduction
Repeated queries (10x same):      ~86% reduction
Dedup hit rate:                   90%+
```

### CSDL-ANLT - Translation Layer
- **ANLT** (Agent-Native Language Translation) for human ↔ CSDL at system edges
- **CBP** (Compressed Binary Protocol) for agent-to-agent wire format
- Human input/output remains natural language
- All 32 agents communicate internally in pure CSDL

### Archon - RAG System
- **Supabase** pgvector for embeddings
- **OpenAI** text-embedding-3-small
- **CSDL-14B** for chat completion
- **Docker** containerized

## Project Structure

```
E3/
├── .claude/                 # Claude Code configuration
│   └── .clauderules         # Project rules and context
├── CSDL-14B/                # Model documentation
│   └── docs/                # Protocol specs, training guides
├── CSDL-ANLT/               # Translation layer
│   ├── csdl-server.py       # Ollama-compatible API server
│   └── src/cbp/             # CBP compression protocol
├── E3-DevMind-AI/           # 32-agent swarm
│   ├── agents/              # Agent implementations + AG-UI server
│   ├── ui/                  # CopilotKit React frontend
│   └── ux/                  # UX improvements
├── Scripts/                 # Startup/stop scripts
│   ├── start-e3-full-stack.sh
│   ├── start-e3-devmind-swarm.sh
│   └── stop-e3-full-stack.sh
├── docs/                    # Documentation
│   └── E3-DEVMIND-ARCHITECTURE.md
├── csdl-14b-f16.gguf        # Model file (28GB, gitignored)
└── .env                     # Environment variables (gitignored)
```

## Hardware Requirements

### Minimum
- 16GB RAM
- 8GB GPU VRAM
- 50GB storage

### Recommended (Current Setup)
- **NVIDIA DGX Spark**
- Grace Blackwell GB10 GPU
- 128GB unified memory
- 20 ARM cores
- CUDA 13.0

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
GITHUB_TOKEN=your_token
OPENAI_API_KEY=your_key  # For Archon embeddings

# Services
CSDL_SERVER_URL=http://localhost:5000
CSDL_SERVER_PORT=5000
E3_AGUI_PORT=8100
E3_UI_PORT=3000
```

## Desktop Launchers

| Launcher | Description |
|----------|-------------|
| **Start E3 Full Stack** | CSDL + Archon + AG-UI + DevMind UI |
| **Start E3 DevMind Swarm** | AG-UI + DevMind UI (requires Full Stack) |
| **Stop E3 Full Stack** | Stop all services |
| **Archon Web UI** | Open Archon admin (localhost:3737) |

## API Endpoints

### CSDL-14B Server (Port 5000)
```bash
# Health check
curl http://localhost:5000/api/tags

# Chat completion (Ollama-compatible)
curl http://localhost:5000/api/chat -d '{
  "model": "csdl-14b",
  "messages": [{"role": "user", "content": "Hello"}]
}'
```

### AG-UI Server (Port 8100)
```bash
# Info endpoint
curl http://localhost:8100/info

# Health check
curl http://localhost:8100/health
```

## Logs

| Service | Log File |
|---------|----------|
| CSDL Server | `/tmp/csdl-server.log` |
| AG-UI Server | `/tmp/e3-agui-server.log` |
| DevMind UI | `/tmp/e3-ui.log` |
| Archon | `docker logs archon-api` |

## Documentation

- **[Architecture](docs/E3-DEVMIND-ARCHITECTURE.md)** - Full system documentation
- **[CSDL Protocol](CSDL-14B/docs/CSDL_PROTOCOL.md)** - Compression protocol spec
- **[ANLT Layer](CSDL-ANLT/docs/03_CSDL_ANLT_README.md)** - Translation layer

## License

- **E3 Platform**: MIT License
- **CSDL-14B**: Apache 2.0 (Base: Qwen License)
- **E3-DevMind-AI**: Proprietary (E3 Consortium)

## Repository

- **URL**: https://github.com/bodhifreeman-ux/E3
- **Branch**: main

---

*E3 - Emergent Engineering Environment*
