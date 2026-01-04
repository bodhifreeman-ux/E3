#!/bin/bash

# Health Check Script for E3 DevMind AI

echo ""
echo "🏥 E3 DevMind AI - Health Check"
echo "==============================="
echo ""

# Check REST API
echo "Checking REST API..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health)

if [ "$API_STATUS" = "200" ]; then
    echo "   ✅ REST API: Healthy"
else
    echo "   ❌ REST API: Unhealthy (Status: $API_STATUS)"
fi

# Check CSDL-vLLM
echo ""
echo "Checking CSDL-vLLM..."
VLLM_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health)

if [ "$VLLM_STATUS" = "200" ]; then
    echo "   ✅ CSDL-vLLM: Healthy"
else
    echo "   ❌ CSDL-vLLM: Unhealthy (Status: $VLLM_STATUS)"
fi

# Check Qdrant
echo ""
echo "Checking Qdrant..."
QDRANT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:6333/collections)

if [ "$QDRANT_STATUS" = "200" ]; then
    echo "   ✅ Qdrant: Healthy"
else
    echo "   ❌ Qdrant: Unhealthy (Status: $QDRANT_STATUS)"
fi

# Check PostgreSQL
echo ""
echo "Checking PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U devmind &> /dev/null; then
    echo "   ✅ PostgreSQL: Healthy"
else
    echo "   ❌ PostgreSQL: Unhealthy"
fi

# Check Redis
echo ""
echo "Checking Redis..."
if [ "$(docker-compose exec -T redis redis-cli ping 2>/dev/null)" = "PONG" ]; then
    echo "   ✅ Redis: Healthy"
else
    echo "   ❌ Redis: Unhealthy"
fi

# Check Docker containers
echo ""
echo "Checking Docker containers..."
docker-compose ps

echo ""
echo "==============================="
echo "Health check complete!"
echo ""
