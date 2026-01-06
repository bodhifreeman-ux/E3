# E3 Project Structure

```
E3/
├── README.md                          # Project overview
├── PROJECT-STRUCTURE.md               # This file
├── LICENSE
│
├── CSDL-14B/                          # CSDL-14B model files (SafeTensors)
│   ├── model/merged_16bit/            # 28GB FP16 model
│   └── docs/
│       ├── 04_CSDL_14B_README.md      # Model specs
│       ├── CSDL-MODEL-DIAGNOSTIC.md   # Tokenization bug investigation
│       ├── CSDL_PROTOCOL.md
│       ├── INSTALLATION.md
│       └── TRAINING.md
│
├── CSDL-ANLT/                         # CSDL server (ANLT provides translation layer)
│   ├── README.md                      # CSDL server setup guide
│   ├── csdl-server.py                 # CSDL inference server (FastAPI)
│   ├── csdl-venv/                     # Python environment
│   └── docs/
│       ├── 03_CSDL_ANLT_README.md     # ANLT translation layer overview
│       └── DGX_Spark_ANLT_Source.md
│
├── E3-DevMind-AI/                     # 32-agent cognitive swarm
│   └── docs/
│       ├── 06_Archon_README.md
│       ├── API_REFERENCE.md
│       ├── DEPLOYMENT.md
│       └── DGX_SPARK_SETUP.md
│
├── llama.cpp/                         # llama.cpp build (has tokenization bug on ARM64)
│
├── docs/                              # Project-level documentation
│   ├── 00_CLAUDE.md                   # Project context
│   ├── 01_ROOT_README.md
│   ├── 02_CSDL_Agent_UI_README.md
│   ├── CSDL-LLAMA-SERVER-SETUP.md
│   ├── DGX_Spark_CSDL_Setup.md
│   └── PYTORCH-BUILD-GUIDE.md
│
├── Scripts/
│   ├── build-pytorch-cuda.sh          # Build PyTorch with CUDA 13.0 (requires sudo)
│   ├── build-pytorch-nosudo.sh        # Build PyTorch (no sudo version)
│   ├── convert-csdl-to-gguf.sh        # Convert SafeTensors to GGUF
│   └── start-llama-server.sh          # Start llama-server (broken on ARM64)
│
└── Model Files
    └── csdl-14b-f16.gguf              # 28GB GGUF (for llama.cpp - broken)
```

## Current Status

✅ **Model is functional** - fine-tuning succeeded
❌ **llama.cpp has tokenization bug** on ARM64 + Blackwell
🔧 **Solution:** Build PyTorch with CUDA (see `build-pytorch-cuda.sh`)

## Quick Start

### Option 1: Build PyTorch (Recommended)
```bash
cd Scripts
./build-pytorch-nosudo.sh
# Wait 2-4 hours
# Then use CSDL-ANLT/csdl-server.py
```

### Option 2: Use llama.cpp from Geekom
Get working llama.cpp version from Geekom and build here.

## Documentation

- **Project context:** [docs/00_CLAUDE.md](docs/00_CLAUDE.md)
- **PyTorch build:** [docs/PYTORCH-BUILD-GUIDE.md](docs/PYTORCH-BUILD-GUIDE.md)
- **CSDL-14B diagnostics:** [CSDL-14B/docs/CSDL-MODEL-DIAGNOSTIC.md](CSDL-14B/docs/CSDL-MODEL-DIAGNOSTIC.md)
- **CSDL server setup:** [CSDL-ANLT/README.md](CSDL-ANLT/README.md)
