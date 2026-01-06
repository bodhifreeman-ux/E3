# CSDL Agent UI Platform

**A comprehensive AI agent development and management platform powered by CSDL (Compressed Semantic Data Language) and ANLT (Agent-Native Language Translation).**

---

## Overview

The CSDL Agent UI Platform is a full-stack application for building, testing, and deploying AI agents with advanced token compression capabilities. It features a premium futuristic interface with collapsible sidebar navigation, real-time system monitoring, and integration with multiple AI services.

### What is CSDL?

**CSDL (Compressed Semantic Data Language)** is an agent-native compressed language format designed to reduce token consumption in AI workflows. Unlike traditional compression methods, CSDL preserves semantic meaning while achieving significant token reduction.

### What is ANLT?

**ANLT (Agent-Native Language Translation)** is the bidirectional translation layer between human-readable language and CSDL. It enables:
- Text → CSDL compression (40-50% token reduction baseline, enhanced targeting 70%+)
- CSDL → Text decompression (semantic reconstruction)
- Real-time compression metrics and analysis

---

## Key Features

### 1. Premium Futuristic UI

- **Futuristic Header**: Animated gradient branding with navigation tabs
- **Collapsible Sidebar**: Quick access to Archon Knowledge and Settings
- **Dark Theme**: Midnight purple gradient with glass-morphism effects
- **Responsive Design**: Works seamlessly on desktop and tablet

### 2. Multi-Agent System (Atlas)

**Atlas Strategic Advisor** - A 5-agent reasoning system for strategic planning:

- **Analyzer**: Breaks down complex problems into components
- **Strategist**: Generates multiple strategic approaches
- **Critic**: Identifies risks and challenges
- **Synthesizer**: Combines insights into actionable plans
- **Reflector**: Ensures alignment with goals and values

### 3. Agent Workspace

Interactive chat interface for conversing with AI agents:
- Real-time agent selection with CSDL compression indicators
- Message history with streaming responses
- Support for both single-agent and multi-agent systems

### 4. Testing Lab

Compare agent performance with and without CSDL compression:
- Side-by-side evaluation results
- Token savings metrics
- Cost analysis per query

### 5. Analytics Dashboard

Monitor system performance and W&B experiment tracking:
- Run statistics and success rates
- Cost tracking over time
- Performance metrics visualization

### 6. Settings & Configuration

Comprehensive settings page with:
- **System Status**: Real-time health monitoring of all services
- **Model Configuration**: Ollama model selection with size/date info
- **Platform Features**: View enabled feature flags
- **Appearance**: Theme selection and notification preferences
- **API Endpoints**: Quick reference for all service URLs

### 7. Archon Knowledge Integration

RAG-powered knowledge retrieval system:
- Document ingestion and indexing
- Semantic search capabilities
- Knowledge-enhanced agent responses

---

## Architecture

### Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18 with TypeScript
- Tailwind CSS + Custom animations
- Lucide React icons

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL (persistent storage)
- Redis (caching)
- Qdrant (vector database)

**AI/ML:**
- Ollama (local LLM inference)
- OpenAI API (optional)
- Sentence Transformers (embeddings)
- CSDL compression algorithms

### Project Structure

```
CSDL-Agent-UI/
├── platform/
│   ├── frontend/                    # Next.js frontend
│   │   ├── app/
│   │   │   ├── dashboard/           # Main application routes
│   │   │   │   ├── page.tsx         # Dashboard
│   │   │   │   ├── workspace/       # Agent chat workspace
│   │   │   │   ├── agents/          # Agent catalog
│   │   │   │   ├── lab/             # Testing lab
│   │   │   │   ├── analytics/       # Analytics dashboard
│   │   │   │   ├── settings/        # Settings page
│   │   │   │   └── layout.tsx       # Sidebar layout
│   │   │   └── page.tsx             # Landing page
│   │   ├── components/
│   │   │   └── ui/                  # Premium UI components
│   │   │       └── core/
│   │   │           └── PageHeader.tsx
│   │   └── package.json
│   │
│   └── backend/                     # FastAPI backend
│       ├── app/
│       │   ├── api/                 # API endpoints
│       │   ├── core/                # Core services & config
│       │   ├── integrations/        # Agent implementations
│       │   ├── services/            # Business logic
│       │   └── main.py              # FastAPI app
│       └── requirements.txt
│
├── CSDL-vLLM/                       # Agent-native LLM (research)
└── README.md                        # This file
```

---

## Installation & Setup

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **PostgreSQL** 14+
- **Redis** 6+
- **Ollama** (for local LLM inference)
- **Docker** (optional, for containerized setup)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LUBTFY/CSDL-Agent-UI.git
   cd CSDL-Agent-UI/platform
   ```

2. **Backend setup:**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Create .env file (copy from .env.example and configure)
   cp .env.example .env

   # Start backend server
   uvicorn app.main:app --reload --port 8000
   ```

3. **Frontend setup** (new terminal):
   ```bash
   cd frontend

   # Install dependencies
   npm install

   # Start development server
   npm run dev
   ```

4. **Start Ollama** (new terminal):
   ```bash
   ollama serve
   # In another terminal, pull a model:
   ollama pull qwen2.5:7b-instruct-q4_K_M
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000/dashboard
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Navigation

### Header Tabs
- **Dashboard**: Overview of system metrics and quick actions
- **Workspace**: Chat interface for interacting with agents
- **Agent Catalog**: Browse and manage available agents
- **Testing Lab**: Run comparisons with/without compression
- **Analytics**: View performance metrics and W&B experiments
- **Archon Knowledge**: External link to RAG knowledge UI (amber highlight)

### Sidebar (Collapsible)
- **Archon Knowledge**: Quick access to knowledge system
- **Settings**: System configuration and preferences

---

## Agents

### Available Agents

| Agent | Type | CSDL Support | Description |
|-------|------|--------------|-------------|
| **Atlas** | Multi-Agent | Yes | 5-agent strategic reasoning system |
| **LUBTFY Agency** | Multi-Agent | Yes | Full-service marketing agency |
| **Shopify Agent** | Specialist | No | E-commerce store management |
| **Video Tutorial** | Specialist | No | Video content generation |
| **NEXUS** | Single | No | Agent code generator |

### Registering Custom Agents

```python
# app/integrations/register_my_agent.py

from app.core.agent_registry import (
    register_agent,
    AgentMetadata,
    AgentType,
    AgentCapability,
)

def register_my_agent():
    metadata = AgentMetadata(
        agent_id="my-agent-v1",
        name="My Custom Agent",
        description="Description of what your agent does",
        agent_type=AgentType.SINGLE,
        version="1.0.0",
        capabilities=[AgentCapability.ANALYSIS],
        supports_compression=True,
        icon="brain",
        color="#3B82F6"
    )
    register_agent(metadata, my_agent_evaluator)
```

---

## Configuration

### Environment Variables

Key environment variables for the backend (`.env`):

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/jarvis_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M

# Feature Flags
ENABLE_DUAL_VIEW=true
ENABLE_COST_TRACKING=true
ENABLE_BENCHMARKS=true

# API Keys (optional)
OPENAI_API_KEY=your-key-here
WANDB_API_KEY=your-key-here
```

---

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health status and feature flags |
| `/info` | GET | Application information |
| `/api/agents` | GET | List all registered agents |
| `/api/evaluate/compare` | POST | Run compression comparison |
| `/api/translate/to-csdl` | POST | Translate text to CSDL |

### Full API documentation: http://localhost:8000/docs

---

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Backend (Python)
cd backend
black app/
isort app/

# Frontend (TypeScript)
cd frontend
npm run lint
```

---

## Performance

### Token Savings (Real Data)

**Atlas Multi-Agent System** with v2_enhanced compression:

- **Standard compression**: ~30% reduction in prompts
- **Inter-agent compression**: ~70% reduction in agent communication
- **Total savings**: 3,000-5,000 tokens per query (at scale)

### Cost Impact

At Ollama (free local inference):
- **Cost**: $0.00 per query
- **Speed**: 50-100 tokens/second (depending on hardware)

---

## Roadmap

- [x] Premium futuristic UI
- [x] Collapsible sidebar navigation
- [x] Settings page with system status
- [x] Ollama model selection
- [x] Archon Knowledge integration
- [ ] Theme persistence (localStorage)
- [ ] Real-time notification system
- [ ] Docker Compose setup
- [ ] Kubernetes deployment manifests

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **CSDL Framework** - Agent-native compression format
- **ANLT** - Agent-Native Language Translation layer
- **Ollama** - Local LLM inference
- **Archon** - RAG knowledge system

---

## Support

For questions, issues, or feature requests:

- **Issues**: https://github.com/LUBTFY/CSDL-Agent-UI/issues
- **Discussions**: https://github.com/LUBTFY/CSDL-Agent-UI/discussions

---

**Built with focus on demonstrating real compression value in multi-agent AI systems.**
