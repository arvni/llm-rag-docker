# Comprehensive health check
#!/bin/bash

set -e

echo "🏥 RAG System Health Check"
echo "=========================="

exit_code=0

# Function to check service health
check_service() {
    local service_name=$1
    local check_command=$2
    local description=$3
    
    echo -n "Checking $description... "
    if eval "$check_command" > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
        exit_code=1
    fi
}

# Docker services
check_service "docker" "docker info" "Docker daemon"
check_service "compose" "docker-compose ps" "Docker Compose"

# Application services
check_service "ollama" "curl -f http://localhost:11434/api/tags" "Ollama API"
check_service "rag-app" "curl -f http://localhost:8501/_stcore/health" "RAG Application"
check_service "filebrowser" "curl -f http://localhost:8080" "File Browser"
check_service "nginx" "curl -f http://localhost:80/health" "Nginx Proxy"
check_service "redis" "docker-compose exec -T redis redis-cli ping" "Redis Cache"
check_service "postgres" "docker-compose exec -T postgres pg_isready -U raguser" "PostgreSQL Database"

# GPU check
echo -n "Checking GPU availability... "
if nvidia-smi > /dev/null 2>&1; then
    echo "✅ Available"
else
    echo "⚠️  Not available"
fi

# Disk space check
echo -n "Checking disk space... "
available_space=$(df / | tail -1 | awk '{print $4}')
if [ "$available_space" -gt 1048576 ]; then  # 1GB in KB
    echo "✅ Sufficient ($(($available_space / 1024 / 1024))GB free)"
else
    echo "⚠️  Low disk space ($(($available_space / 1024))MB free)"
fi

# Memory check
echo -n "Checking memory usage... "
mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$mem_usage" -lt 90 ]; then
    echo "✅ Normal (${mem_usage}% used)"
else
    echo "⚠️  High memory usage (${mem_usage}% used)"
fi

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 All systems healthy!"
else
    echo "⚠️  Some issues detected. Check logs for details."
fi

exit $exit_code