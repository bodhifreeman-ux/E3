# E3

E3 infrastructure and agentic architecture - A comprehensive AI development platform integrating fine-tuned models with multi-agent systems.

## Overview

E3 is a parent repository containing:

- **[csdl-14b](csdl-14b/)** - Fine-tuned 14B parameter LLM for Compressed Semantic Data Language
- **[E3-DevMind-AI](E3-DevMind-AI/)** - 36 multi-agent system for autonomous AI development
- **llama.cpp** - CUDA-optimized inference engine for Grace Blackwell GPU

## Architecture

### CSDL-14B Model
- **Base Model**: Qwen2.5-14B-Instruct
- **Parameters**: 14.7 billion
- **Format**: SafeTensors F16 / GGUF
- **Specialization**: Binary protocol for AI agent communication (90-98% token reduction)
- **Hardware**: Optimized for NVIDIA Grace Blackwell (128GB unified memory)

### E3-DevMind-AI
- **Agents**: 36 specialized multi-agent system
- **Core**: CSDL protocol integration
- **Features**: Autonomous development, code generation, project management
- **Integration**: GitHub, Jira, Slack, and more

## Quick Start

### Prerequisites

- NVIDIA Grace Blackwell GPU (or compatible CUDA 13.0+ GPU)
- 128GB+ RAM
- Ubuntu 22.04+ (or compatible Linux distribution)
- Python 3.11+
- Git with LFS

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/bodhifreeman-ux/E3.git
cd E3
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Setup llama-server** (once model files are copied)
```bash
# Convert model to GGUF format
./convert-csdl-to-gguf.sh

# Start the server
./start-llama-server.sh
```

Or use the desktop launchers:
- **Start CSDL Llama Server** - Launch the inference server
- **Stop CSDL Llama Server** - Stop the running server

### Running llama-server

The server will start on `http://localhost:8002` with:
- Full GPU acceleration (all layers on Grace Blackwell)
- 4096 token context window
- OpenAI-compatible API endpoints

## Project Structure

```
E3/
├── csdl-14b/              # Fine-tuned CSDL model repository
│   ├── docs/              # Documentation (protocol, training, installation)
│   ├── examples/          # Usage examples
│   ├── modelfiles/        # Ollama model configurations
│   └── models/            # Model files (gitignored)
├── E3-DevMind-AI/         # Multi-agent development system
│   ├── agents/            # Agent implementations
│   ├── csdl/              # CSDL protocol handlers
│   ├── devmind_core/      # Core system
│   ├── deployment/        # Deployment configurations
│   └── setup_dgx_spark.sh # DGX Spark setup script
├── llama.cpp/             # CUDA-optimized inference engine
├── .env                   # Environment configuration (gitignored)
├── .env.example           # Environment template
├── convert-csdl-to-gguf.sh   # Model conversion script
├── start-llama-server.sh     # Server startup script
└── CSDL-LLAMA-SERVER-SETUP.md # Detailed setup guide
```

## Environment Variables

See [.env.example](.env.example) for all available configuration options.

### Required
- `GITHUB_TOKEN` - GitHub personal access token
- `GITHUB_USERNAME` - Your GitHub username

### Optional (for extended features)
- `OPENAI_API_KEY` - OpenAI API for multimodal features
- `ANTHROPIC_API_KEY` - Anthropic Claude API
- `JIRA_*` - Jira integration
- `SLACK_*` - Slack integration
- See `.env.example` for full list

## Hardware Recommendations

### Minimum
- 12GB RAM
- 8GB GPU VRAM
- 100GB storage

### Recommended (DGX Spark)
- NVIDIA Grace Blackwell GB10
- 128GB unified memory
- 500GB+ NVMe storage
- CUDA 13.0+

## Documentation

- **[CSDL Protocol](csdl-14b/docs/CSDL_PROTOCOL.md)** - Protocol specification
- **[Training Guide](csdl-14b/docs/TRAINING.md)** - Model training details
- **[Installation](csdl-14b/docs/INSTALLATION.md)** - Installation instructions
- **[Server Setup](CSDL-LLAMA-SERVER-SETUP.md)** - llama-server configuration

## Performance

With Grace Blackwell GPU:
- **Model Size**: 28GB (F16 GGUF)
- **Inference Speed**: Near-instantaneous (all layers on GPU)
- **Token Compression**: 90-98% with CSDL protocol
- **Context Window**: 4096 tokens (expandable)

## License

MIT License - See individual component licenses:
- CSDL-14B: Apache 2.0 (base model: Qwen License)
- E3-DevMind-AI: MIT License
- llama.cpp: MIT License

## Contributing

This is a private repository. For access or collaboration inquiries, contact the repository owner.

## Support

For issues or questions:
- Open an issue in the respective component repository
- Check component documentation in `docs/` directories

## Roadmap

- [x] CSDL-14B model fine-tuning
- [x] llama.cpp CUDA integration for Grace Blackwell
- [x] Desktop launcher creation
- [x] Environment configuration
- [ ] Complete model file transfer (in progress)
- [ ] Model conversion to GGUF F16
- [ ] E3-DevMind-AI integration with CSDL-14B
- [ ] Multi-agent system deployment
- [ ] Production deployment on DGX Spark

---

**E3 - Empowering AI Development with Advanced Multi-Agent Systems**
