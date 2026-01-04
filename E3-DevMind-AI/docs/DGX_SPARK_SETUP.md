# DGX Spark Complete Setup Guide

## One-Command Installation for E3 DevMind AI on NVIDIA DGX Spark

This guide provides automated, one-command installation of the complete E3 DevMind AI system on NVIDIA DGX Spark.

---

## 📋 What This Script Does

The automated `setup_dgx_spark.sh` script will:

- ✅ Install all system dependencies
- ✅ Install Docker & NVIDIA Container Toolkit
- ✅ Install Python 3.11 & required packages
- ✅ Setup CSDL-vLLM (CSDL-optimized inference)
- ✅ Setup E3 DevMind AI (all 32 agents)
- ✅ Configure environment variables
- ✅ Initialize databases (PostgreSQL, Qdrant, Redis)
- ✅ Start all services
- ✅ Verify installation
- ✅ Configure systemd service
- ✅ Install CLI tools

**Total Time**: ~30-45 minutes (mostly unattended)

---

## 🚀 Quick Start

### Option 1: One-Liner Install (Easiest)

```bash
curl -fsSL https://raw.githubusercontent.com/LUBTFY/E3-DevMind-AI/main/setup_dgx_spark.sh | sudo bash
```

### Option 2: Download and Run

```bash
# Download script
wget https://raw.githubusercontent.com/LUBTFY/E3-DevMind-AI/main/setup_dgx_spark.sh

# Make executable
chmod +x setup_dgx_spark.sh

# Run
sudo ./setup_dgx_spark.sh
```

### Option 3: Git Clone and Install

```bash
git clone https://github.com/LUBTFY/E3-DevMind-AI.git
cd E3-DevMind-AI
sudo ./setup_dgx_spark.sh
```

---

## ⏱️ Installation Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| System update | ~5 min | Update Ubuntu packages |
| Docker install | ~3 min | Install Docker Engine + Compose |
| Python setup | ~2 min | Install Python 3.11 |
| Repository cloning | ~2 min | Clone 3 repositories |
| **Docker image building** | **~15-20 min** | Build CSDL-vLLM & DevMind images |
| Database initialization | ~3 min | Setup PostgreSQL, Qdrant, Redis |
| Service startup | ~5 min | Start all services |
| Verification | ~2 min | Health checks |

**Total**: ~30-45 minutes

---

## 📦 What Gets Installed

### System Packages

- Docker CE (latest)
- Docker Compose v2
- NVIDIA Container Toolkit
- Python 3.11
- Build tools (gcc, make, etc.)
- Git, curl, wget

### Docker Containers

- **CSDL-vLLM**: CSDL-optimized inference engine
- **E3 DevMind AI**: Main application (32 agents)
- **PostgreSQL**: Metadata storage
- **Qdrant**: Vector database (knowledge system)
- **Redis**: Cache and message broker

### Directories Created

```
/opt/e3-devmind-ai/
├── CSDL-vLLM/                    # CSDL inference engine
├── e3-devmind-ai/                # Main application
├── agent-native-language-compiler/ # ANLT compiler
├── data/
│   ├── qdrant/                   # Vector database
│   ├── postgres/                 # SQL database
│   └── redis/                    # Cache
├── logs/                         # Application logs
├── knowledge/                    # Knowledge base
└── models/                       # ML models
```

### User & Permissions

- User: `devmind`
- Group: `devmind`
- Docker group membership
- systemd service: `e3-devmind.service`

---

## 🔧 Post-Installation Configuration

### 1. Configure API Keys

After installation, you **must** add your API keys:

```bash
sudo nano /opt/e3-devmind-ai/e3-devmind-ai/.env
```

**Required keys**:

```bash
# For multimodal capabilities (required)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# For integrations (optional)
GITHUB_TOKEN=ghp_your-github-token
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-token
```

### 2. Restart Services

After adding API keys:

```bash
cd /opt/e3-devmind-ai/e3-devmind-ai
docker compose restart
```

### 3. Verify Services

```bash
# Check all services
devmind-status

# Run health checks
devmind-health

# View logs
devmind-logs
```

---

## 🎯 Using E3 DevMind AI

### Web Interface

Open your browser to:

```
http://YOUR_DGX_IP:8000
```

**Available endpoints**:

- **Dashboard**: `http://YOUR_DGX_IP:8000`
- **API Docs**: `http://YOUR_DGX_IP:8000/docs`
- **REST API**: `http://YOUR_DGX_IP:8000/api`
- **WebSocket**: `ws://YOUR_DGX_IP:8001/ws`

### CLI Interface

The installer creates convenient aliases and a `devmind` CLI:

```bash
# Ask a question
devmind ask "What are the key risks in our current sprint?"

# Check system status
devmind status

# List all agents
devmind agents

# Query knowledge base
devmind kb-search "authentication implementation"

# Get knowledge stats
devmind kb-stats

# Interactive REPL
devmind repl
```

### Docker Compose Commands

```bash
# Start all services
devmind-start

# Stop all services
devmind-stop

# View logs (follow mode)
devmind-logs

# Check service status
devmind-status

# Run health check
devmind-health
```

### Systemd Service

```bash
# Start on boot
sudo systemctl enable e3-devmind

# Start now
sudo systemctl start e3-devmind

# Stop
sudo systemctl stop e3-devmind

# Check status
sudo systemctl status e3-devmind
```

---

## 🛠️ Troubleshooting

### Installation Failed

View the full installation log:

```bash
sudo cat /var/log/e3-devmind-setup.log
```

### GPU Not Detected

Verify NVIDIA drivers:

```bash
nvidia-smi
```

Test GPU in Docker:

```bash
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

### Services Won't Start

Check Docker:

```bash
sudo systemctl status docker
```

Check specific service logs:

```bash
cd /opt/e3-devmind-ai/e3-devmind-ai
docker compose logs devmind
docker compose logs csdl-vllm
docker compose logs postgres
```

Restart everything:

```bash
cd /opt/e3-devmind-ai/e3-devmind-ai
docker compose down
docker compose up -d
```

### API Not Responding

Check if service is running:

```bash
docker compose ps
```

Check API logs:

```bash
docker compose logs devmind
```

Verify port is listening:

```bash
netstat -tlnp | grep 8000
```

### Database Connection Issues

Check PostgreSQL:

```bash
docker compose exec postgres pg_isready -U devmind
```

Check Qdrant:

```bash
curl http://localhost:6333/collections
```

Check Redis:

```bash
docker compose exec redis redis-cli ping
```

### Permission Errors

Fix ownership:

```bash
sudo chown -R devmind:devmind /opt/e3-devmind-ai
```

### Out of Disk Space

Check space:

```bash
df -h
```

Clean Docker:

```bash
docker system prune -a
```

---

## 🔒 Security Considerations

### Firewall

The script configures UFW (if available):

```bash
# Check firewall status
sudo ufw status

# Manually allow ports if needed
sudo ufw allow 8000/tcp comment "E3 DevMind API"
sudo ufw allow 8001/tcp comment "E3 DevMind WebSocket"
```

### API Keys

- Stored in `/opt/e3-devmind-ai/e3-devmind-ai/.env`
- File permissions: `600` (owner read/write only)
- **Never commit .env to git**

### Network Access

By default, services bind to `0.0.0.0` (all interfaces).

To restrict to localhost only, edit `.env`:

```bash
API_HOST=127.0.0.1
```

Then restart:

```bash
docker compose restart
```

---

## 📊 System Requirements

### Minimum Requirements

- **OS**: Ubuntu 22.04 LTS
- **CPU**: 8 cores
- **RAM**: 32 GB
- **Storage**: 200 GB SSD
- **GPU**: NVIDIA GPU with 24GB+ VRAM
- **Network**: 1 Gbps

### Recommended (DGX Spark)

- **CPU**: NVIDIA Grace (144 cores)
- **RAM**: 480 GB
- **Storage**: 4 TB NVMe
- **GPU**: NVIDIA Blackwell GB10 (1 PETAFLOP)
- **Network**: 10 Gbps

---

## 🔄 Updating E3 DevMind AI

### Pull Latest Changes

```bash
cd /opt/e3-devmind-ai/e3-devmind-ai
sudo -u devmind git pull
```

### Rebuild Images

```bash
docker compose build
docker compose up -d
```

### Full Reinstall

Re-run the setup script:

```bash
sudo ./setup_dgx_spark.sh
```

The script is idempotent and will:
- Skip already installed packages
- Update existing repositories
- Preserve your `.env` file

---

## 📝 Uninstallation

To completely remove E3 DevMind AI:

```bash
# Stop services
cd /opt/e3-devmind-ai/e3-devmind-ai
docker compose down -v

# Remove systemd service
sudo systemctl stop e3-devmind
sudo systemctl disable e3-devmind
sudo rm /etc/systemd/system/e3-devmind.service
sudo systemctl daemon-reload

# Remove Docker images
docker rmi csdl-vllm:latest
docker rmi e3-devmind-ai:latest

# Remove installation directory
sudo rm -rf /opt/e3-devmind-ai

# Remove user
sudo userdel -r devmind

# Remove CLI
sudo rm /usr/local/bin/devmind
```

---

## 🎉 What You Get After Installation

✅ **Fully configured DGX Spark** ready for AI workloads
✅ **Docker with GPU support** for containerized deployment
✅ **CSDL-vLLM running** with 70-90% token compression
✅ **E3 DevMind AI running** with all 32 agents active
✅ **All databases initialized** (PostgreSQL, Qdrant, Redis)
✅ **CLI tools installed** for easy interaction
✅ **Systemd service configured** for auto-start on boot
✅ **Web interface accessible** for dashboard and API
✅ **Health monitoring** with automated checks
✅ **Production-ready deployment** with logging and error handling

**Total manual effort**: ~5 minutes (just add API keys!)

---

## 📚 Additional Resources

- **API Reference**: See `docs/API_REFERENCE.md`
- **Deployment Guide**: See `docs/DEPLOYMENT.md`
- **Architecture**: See main `README.md`
- **CSDL Protocol**: See CSDL-vLLM repository
- **ANLT Compiler**: See agent-native-language-compiler repository

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: `/var/log/e3-devmind-setup.log`
2. **Check service logs**: `docker compose logs`
3. **Run health check**: `devmind-health`
4. **Open an issue**: GitHub Issues
5. **Contact support**: E3 Consortium

---

## ✅ Installation Checklist

After running the script, verify:

- [ ] Docker is installed and running
- [ ] NVIDIA Container Toolkit is configured
- [ ] Python 3.11 is default
- [ ] Repositories are cloned
- [ ] `.env` file is configured with API keys
- [ ] Docker images are built
- [ ] All services are running (`docker compose ps`)
- [ ] Health checks pass (`devmind-health`)
- [ ] CLI works (`devmind status`)
- [ ] Web interface is accessible
- [ ] systemd service is enabled

---

**Save this script and deploy E3 DevMind AI on any DGX Spark in under an hour!**
