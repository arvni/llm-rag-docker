# Stop all services
#!/bin/bash

set -e

echo "🛑 Stopping RAG System..."

# Stop containers
echo "📦 Stopping containers..."
docker-compose down

# Optional: Remove volumes (uncomment to delete all data)
# echo "🗑️  Removing volumes..."
# docker-compose down -v

# Clean up unused images
echo "🧹 Cleaning up..."
docker image prune -f

echo "✅ RAG System stopped successfully!"

# scripts/status.sh - System status check
#!/bin/bash

set -e

echo "📊 RAG System Status Report"
echo "============================"

# Container status
echo ""
echo "🐳 Container Status:"
docker-compose ps

# Resource usage
echo ""
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Volume usage
echo ""
echo "💾 Volume Usage:"
docker system df

# Service health checks
echo ""
echo "🏥 Health Checks:"

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "  ✅ Ollama: Healthy"
    # List models
    echo "  🤖 Available Models:"
    docker-compose exec -T ollama ollama list | grep -v "NAME" | awk '{print "    • " $1}'
else
    echo "  ❌ Ollama: Unhealthy"
fi

# Check RAG App
if curl -s http://localhost:8501/_stcore/health > /dev/null; then
    echo "  ✅ RAG App: Healthy"
else
    echo "  ❌ RAG App: Unhealthy"
fi

# Check File Browser
if curl -s http://localhost:8080 > /dev/null; then
    echo "  ✅ File Browser: Healthy"
else
    echo "  ❌ File Browser: Unhealthy"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "  ✅ Redis: Healthy"
else
    echo "  ❌ Redis: Unhealthy"
fi

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U raguser > /dev/null 2>&1; then
    echo "  ✅ PostgreSQL: Healthy"
else
    echo "  ❌ PostgreSQL: Unhealthy"
fi

# GPU status
echo ""
echo "🎮 GPU Status:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | \
    while IFS=, read -r name mem_used mem_total gpu_util; do
        echo "  🔧 $name: ${mem_used}MB/${mem_total}MB (${gpu_util}% GPU)"
    done
else
    echo "  ❌ NVIDIA SMI not available"
fi

# Log file sizes
echo ""
echo "📝 Log File Sizes:"
if [ -d "logs" ]; then
    du -sh logs/* 2>/dev/null | head -10 || echo "  No log files found"
else
    echo "  No logs directory found"
fi

echo ""
echo "🌐 Access URLs:"
echo "  • Main App: http://localhost:8501"
echo "  • File Manager: http://localhost:8080"
echo "  • API: http://localhost:11434"