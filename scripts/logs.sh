# View system logs
#!/bin/bash

SERVICE=${1:-"all"}

echo "📝 RAG System Logs"
echo "=================="

case $SERVICE in
    "ollama")
        echo "🤖 Ollama Logs:"
        docker-compose logs -f ollama
        ;;
    "rag-app")
        echo "🧠 RAG Application Logs:"
        docker-compose logs -f rag-app
        ;;
    "nginx")
        echo "🌐 Nginx Logs:"
        docker-compose logs -f nginx
        ;;
    "postgres")
        echo "🗄️  PostgreSQL Logs:"
        docker-compose logs -f postgres
        ;;
    "redis")
        echo "🔴 Redis Logs:"
        docker-compose logs -f redis
        ;;
    "all")
        echo "📊 All Service Logs:"
        docker-compose logs -f
        ;;
    *)
        echo "❓ Available services: ollama, rag-app, nginx, postgres, redis, all"
        echo "Usage: ./scripts/logs.sh [service_name]"
        ;;
esac