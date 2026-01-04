# E3 DevMind AI - Deployment Guide

Complete deployment guide for NVIDIA DGX Spark.

## Prerequisites

### Hardware
- NVIDIA DGX Spark with Grace Blackwell GB10
- 1 PETAFLOP of FP4 AI performance
- 128GB unified memory
- 4TB storage

### Software
- Ubuntu 24.04 LTS
- Docker 24.0+
- Docker Compose 2.20+
- NVIDIA Container Toolkit

### Network
- Static IP address
- Open ports: 8000, 8001, 8002, 6333, 5432, 6379

## Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/E3-Consortium/e3-devmind-ai.git
cd e3-devmind-ai
```

### Step 2: Configure Environment
```bash
cp .env.example .env
nano .env
```

**Required Configuration:**
```bash
# API Keys
OPENAI_API_KEY=sk-your-key

# CSDL-vLLM
CSDL_VLLM_URL=http://localhost:8002

# Databases
DATABASE_URL=postgresql://devmind:secure-password@postgres:5432/e3_devmind
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Integrations
GITHUB_TOKEN=ghp_your-token
SLACK_BOT_TOKEN=xoxb-your-token
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@e3.com
JIRA_API_TOKEN=your-jira-token
```

### Step 3: Build CSDL-vLLM
```bash
# Clone CSDL-vLLM repository
cd ..
git clone https://github.com/LUBTFY/CSDL-vLLM.git
cd CSDL-vLLM

# Build Docker image
docker build -t csdl-vllm:latest .

cd ../e3-devmind-ai
```

### Step 4: Deploy
```bash
# Using deployment script
./deployment/scripts/deploy.sh production

# Or manually
docker-compose up -d
```

### Step 5: Verify
```bash
# Health check
./deployment/scripts/health_check.sh

# Check logs
docker-compose logs -f devmind

# Test API
curl http://localhost:8000/api/health
```

## Docker Compose Configuration

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Service Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f devmind
```

### Scale Services
```bash
# Scale Celery workers
docker-compose up -d --scale celery-worker=4
```

## Monitoring

### Service Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

### System Status
```bash
# Via CLI
python -m cli.main status

# Via API
curl http://localhost:8000/api/status
```

## Backup & Recovery

### Backup Knowledge Base
```bash
# Backup Qdrant
docker-compose exec qdrant tar czf /qdrant/storage/backup.tar.gz /qdrant/storage/collections

# Backup PostgreSQL
docker-compose exec postgres pg_dump -U devmind e3_devmind > backup.sql
```

### Restore Knowledge Base
```bash
# Restore Qdrant
docker-compose exec qdrant tar xzf /qdrant/storage/backup.tar.gz -C /qdrant/storage/

# Restore PostgreSQL
docker-compose exec -T postgres psql -U devmind e3_devmind < backup.sql
```

## Troubleshooting

### CSDL-vLLM Not Connecting
```bash
# Check if CSDL-vLLM is running
docker-compose ps csdl-vllm

# Check logs
docker-compose logs csdl-vllm

# Restart
docker-compose restart csdl-vllm
```

### Qdrant Connection Issues
```bash
# Check Qdrant status
curl http://localhost:6333/collections

# Check logs
docker-compose logs qdrant

# Restart
docker-compose restart qdrant
```

### High Memory Usage
```bash
# Check memory usage
docker stats

# Reduce agent count (if needed)
# Edit docker-compose.yml environment:
MAX_CONCURRENT_AGENTS=16
```

### API Slow Response
```bash
# Check CSDL-vLLM performance
curl http://localhost:8002/health

# Check agent status
curl http://localhost:8000/api/agents

# Review logs for bottlenecks
docker-compose logs devmind | grep "slow"
```

## Performance Tuning

### DGX Spark Optimization
```yaml
# docker-compose.yml
services:
  devmind:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

### CSDL-vLLM Performance
```bash
# Increase GPU memory utilization
GPU_MEMORY_UTILIZATION=0.9

# Increase max model length
MAX_MODEL_LEN=8192
```

### Database Optimization
```bash
# PostgreSQL
docker-compose exec postgres psql -U devmind -c "VACUUM ANALYZE;"

# Qdrant
# Optimize vector index
curl -X POST http://localhost:6333/collections/e3_knowledge/optimize
```

## Security

### Enable SSL/TLS
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name devmind.e3.local;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

### Authentication
```python
# Add to api/rest_api.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/query")
async def query_devmind(
    request: QueryRequest,
    token: str = Depends(security)
):
    # Verify token
    # ...
```

## Updating

### Update to Latest Version
```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Deploy
./deployment/scripts/deploy.sh production
```

## Support

For issues or questions:
- Internal Support: devmind-support@e3consortium.com
- Documentation: https://docs.e3devmind.ai
- Status Page: https://status.e3devmind.ai
