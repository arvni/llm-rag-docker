# Update system
#!/bin/bash

set -e

echo "🔄 Updating RAG System..."

# Backup before update
echo "💾 Creating backup..."
./scripts/backup.sh

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose pull

# Rebuild containers
echo "🔨 Rebuilding containers..."
docker-compose up --build -d

# Wait for services
echo "⏳ Waiting for services to restart..."
sleep 30

# Check status
echo "📊 Checking system status..."
./scripts/status.sh

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ Update completed successfully!"
