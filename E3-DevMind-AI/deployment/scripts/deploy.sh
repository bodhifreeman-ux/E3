#!/bin/bash

# E3 DevMind AI Deployment Script
# Deploys to NVIDIA DGX Spark

set -e

echo "🚀 E3 DevMind AI - Deployment Script"
echo "======================================"

# Configuration
DEPLOY_ENV=${1:-production}
DGX_HOST=${DGX_HOST:-dgx-spark.e3.local}
DGX_USER=${DGX_USER:-devmind}
PROJECT_DIR="/opt/e3-devmind-ai"

echo ""
echo "📋 Configuration:"
echo "  • Environment: $DEPLOY_ENV"
echo "  • DGX Host: $DGX_HOST"
echo "  • User: $DGX_USER"
echo "  • Project Dir: $PROJECT_DIR"
echo ""

# Step 1: Pre-deployment checks
echo "1️⃣  Running pre-deployment checks..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker not installed"
    exit 1
fi
echo "   ✅ Docker installed"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not installed"
    exit 1
fi
echo "   ✅ docker-compose installed"

# Step 2: Build Docker images
echo ""
echo "2️⃣  Building Docker images..."
docker-compose build
echo "   ✅ Images built successfully"

# Step 3: Push to registry (production only)
if [ "$DEPLOY_ENV" = "production" ]; then
    echo ""
    echo "3️⃣  Pushing images to registry..."
    docker-compose push
    echo "   ✅ Images pushed to registry"
fi

# Step 4: Copy files to DGX Spark
echo ""
echo "4️⃣  Copying files to DGX Spark..."
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
    --exclude 'generated_agents' --exclude 'logs' \
    ./ ${DGX_USER}@${DGX_HOST}:${PROJECT_DIR}/
echo "   ✅ Files copied successfully"

# Step 5: Deploy on DGX Spark
echo ""
echo "5️⃣  Deploying on DGX Spark..."
ssh ${DGX_USER}@${DGX_HOST} << EOF
set -e

cd ${PROJECT_DIR}

# Load environment
if [ -f .env ]; then
    source .env
fi

# Stop existing containers
echo "   Stopping existing containers..."
docker-compose down

# Pull latest images (if using registry)
if [ "$DEPLOY_ENV" = "production" ]; then
    echo "   Pulling latest images..."
    docker-compose pull
fi

# Start services
echo "   Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "   Waiting for services to be healthy..."
sleep 15

# Check health
echo "   Checking health..."
curl -f http://localhost:8000/api/health || exit 1

echo "   ✅ E3 DevMind AI deployed successfully!"
EOF

# Step 6: Post-deployment verification
echo ""
echo "6️⃣  Running post-deployment verification..."
sleep 5

# Test API health
HEALTH_CHECK=$(curl -s http://${DGX_HOST}:8000/api/health)
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo "   ✅ API health check passed"
else
    echo "   ❌ API health check failed"
    exit 1
fi

# Step 7: Complete
echo ""
echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "🌐 Access E3 DevMind AI:"
echo "   • Web: http://${DGX_HOST}:8000"
echo "   • API: http://${DGX_HOST}:8000/api"
echo "   • Docs: http://${DGX_HOST}:8000/docs"
echo ""
echo "📊 Check status:"
echo "   ssh ${DGX_USER}@${DGX_HOST}"
echo "   cd ${PROJECT_DIR}"
echo "   docker-compose ps"
echo ""
