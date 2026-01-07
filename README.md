# E3 - Emergent Engineering Environment

> AI-powered development platform with 32-agent swarm, local LLM inference, and proprietary CSDL compression protocol

## Current Status

| Component | Status | Port | Description |
|-----------|--------|------|-------------|
| **CSDL-14B Server** | ✅ Running | 5000 | CSDL Protocol Encoding (llama.cpp) |
| **Nemotron Nano 8B** | ⏳ Pending | 5001 | Reasoning Model (llama.cpp) |
| **Safety Guard 8B** | ⏳ Pending | 5002 | Content Moderation (llama.cpp) |
| **AG-UI Server** | ✅ Running | 8100 | Agent-UI Protocol Server |
| **DevMind UI** | ✅ Running | 3000 | CopilotKit React Frontend |
| **Archon RAG** | ✅ Running | 8181, 8051, 3737 | RAG System |

**Hardware**: NVIDIA DGX Spark (Grace Blackwell GB10, 128GB unified memory, CUDA 13.0)
**PyTorch**: Built from source with CUDA 13.0 support for Blackwell architecture

## Hybrid LLM Architecture (NEW)

E3 DevMind now supports a **hybrid multi-model architecture** for optimal performance:

```
Human Query
    │
    ▼
┌─────────────────┐
│  Safety Guard   │  ← Content moderation (port 5002)
│   (8B Nano)     │
└────────┬────────┘
         │ (if safe)
         ▼
┌─────────────────┐
│      ANLT      │  ← Human → CSDL translation
│   (Edge Only)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Nemotron     │  ← High-quality reasoning (port 5001)
│ (8B/30B Nano)  │
└────────┬────────┘
         │ (reasoning)
         ▼
┌─────────────────┐
│   CSDL-14B     │  ← CSDL protocol encoding (port 5000)
│   (Qwen2.5)    │
└────────┬────────┘
         │ (CSDL)
         ▼
┌─────────────────┐
│  32-Agent      │  ← Pure CSDL inter-agent communication
│    Swarm       │
└────────┬────────┘
         │ (CSDL)
         ▼
┌─────────────────┐
│     ANLT       │  ← CSDL → Human translation
│   (Edge Only)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Safety Guard   │  ← Output moderation
│   (8B Nano)     │
└────────┬────────┘
         │
         ▼
    Human Response
```

**Model Roles:**
- **Nemotron Nano**: High-quality reasoning and analysis (optimized for DGX Spark)
- **CSDL-14B**: Protocol encoding/decoding (trained on 32K CSDL examples)
- **Safety Guard**: Content moderation at system edges

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
+================================================================================================+
|                              E3 DEVMIND PLATFORM v2.0                                          |
|                         HYBRID LLM + CSDL-NATIVE ARCHITECTURE                                  |
+================================================================================================+
|                                                                                                |
|    HUMAN INTERFACE LAYER                                                                       |
|    +------------------+      +------------------+      +------------------+                    |
|    |   CopilotKit     |      |     AG-UI        |      |   Safety Guard   |                    |
|    |    React UI      |<---->|     Server       |<---->|    (Port 5002)   |                    |
|    |   (Port 3000)    |      |   (Port 8100)    |      |  Content Filter  |                    |
|    +------------------+      +------------------+      +------------------+                    |
|                                      |                         |                               |
|    EDGE TRANSLATION LAYER            |                         |                               |
|    +-------------------------------------+                     |                               |
|    |              ANLT                    |<--------------------+                               |
|    |     Human ↔ CSDL Translation        |                                                     |
|    |        (Edge Only)                  |                                                     |
|    +-------------------------------------+                                                     |
|                       |                                                                        |
|    HYBRID LLM LAYER   |                                                                        |
|    +------------------+------------------+------------------+                                  |
|    |   Nemotron Nano   |    CSDL-14B     |   Archon RAG    |                                  |
|    |    (Port 5001)    |   (Port 5000)   |  (8181/8051)    |                                  |
|    |   Reasoning &     |   CSDL Format   |  Vector Search  |                                  |
|    |    Analysis       |   Encoding      |  + Embeddings   |                                  |
|    +------------------+------------------+------------------+                                  |
|                       |                                                                        |
|    CSDL PROTOCOL BUS  |                                                                        |
|    +---------------------------------------------------------------------------+              |
|    |                        PURE CSDL MESSAGE BUS                              |              |
|    |   Zero-overhead | Sub-ms latency | 70-90% token reduction                 |              |
|    +---------------------------------------------------------------------------+              |
|                       |                                                                        |
|    32-AGENT COGNITIVE SWARM                                                                    |
|    +------------------+------------------+------------------+------------------+              |
|    |    Tier 1        |     Tier 2       |     Tier 3       |    Tier 4        |              |
|    |   Oracle (1)     |   Strategic (4)  |   Analysis (6)   | Execution (10)   |              |
|    +------------------+------------------+------------------+------------------+              |
|    |    Tier 5        |     Tier 6       |     Tier 7       |                  |              |
|    | Knowledge (6)    |   Project (3)    |   Growth (2)     |                  |              |
|    +------------------+------------------+------------------+------------------+              |
+================================================================================================+
```

### Data Flow (Hybrid Mode)

```
1. Human Input → Safety Guard (content check)
2. Safety Guard → ANLT (Human → CSDL translation)
3. ANLT → Oracle (CSDL query routing)
4. Oracle → Selected Agents (parallel CSDL queries)
   └─ Per Agent: Nemotron(reason) → CSDL-14B(encode)
5. Agents → Oracle (CSDL responses via message bus)
6. Oracle → ANLT (CSDL → Human synthesis)
7. ANLT → Safety Guard (output check)
8. Safety Guard → Human Response
```

## Components

### Hybrid LLM Stack (NEW)

| Model | Port | Purpose | Base | Quantization |
|-------|------|---------|------|--------------|
| **CSDL-14B** | 5000 | CSDL Protocol Encoding | Qwen2.5-14B | F16 |
| **Nemotron Nano** | 5001 | Reasoning & Analysis | NVIDIA 8B/30B | Q4_K_M |
| **Safety Guard** | 5002 | Content Moderation | NVIDIA Aegis | Q4_K_M |

### CSDL-14B - Protocol Encoder
- **Base**: Qwen2.5-14B-Instruct (14.7B parameters)
- **Training**: 32,000+ CSDL compression examples
- **Role**: Encodes natural language reasoning into CSDL format
- **Inference**: llama.cpp (GGUF format)
- **Hardware**: NVIDIA DGX Spark (Grace Blackwell GB10, 128GB unified memory)

### Nemotron Nano - Reasoning Engine
- **Base**: NVIDIA Nemotron Nano 8B V2 (or 30B for higher quality)
- **Role**: High-quality reasoning and analysis for each agent
- **Performance**: ~33 tok/s on DGX Spark (8B), optimized for Grace Blackwell
- **Inference**: llama.cpp with NVFP4 quantization support
- **Flow**: Query → Nemotron(reason) → CSDL-14B(encode) → CSDL Bus

### Safety Guard - Content Moderation
- **Base**: NVIDIA Aegis Content Safety / Llama Guard 3
- **Role**: Input/output content filtering at system edges
- **Checks**: Harmful content, PII, prompt injection, policy violations
- **Latency**: <100ms classification per message

### E3-DevMind-AI - 32-Agent Swarm
- **32 specialized agents** in 7-tier hierarchy
- **Pure CSDL** inter-agent communication
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
│   ├── start-e3-full-stack.sh       # Start all services
│   ├── start-e3-devmind-swarm.sh    # Start DevMind swarm only
│   ├── start-llama-server.sh        # Start CSDL-14B (port 5000)
│   ├── start-nemotron-server.sh     # Start Nemotron reasoning (port 5001)
│   ├── start-nemotron-guard-server.sh # Start Safety Guard (port 5002)
│   ├── download-nemotron-models.sh  # Download Nemotron GGUF models
│   └── stop-e3-full-stack.sh        # Stop all services
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
