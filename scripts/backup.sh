# Backup system data
#!/bin/bash

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/backup_$TIMESTAMP"

echo "💾 Creating system backup..."
echo "📁 Backup location: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup data directories
echo "📄 Backing up data files..."
cp -r data "$BACKUP_DIR/" 2>/dev/null || echo "  No data directory found"
cp -r uploads "$BACKUP_DIR/" 2>/dev/null || echo "  No uploads directory found"
cp -r config "$BACKUP_DIR/" 2>/dev/null || echo "  No config directory found"

# Backup Docker volumes
echo "🐳 Backing up Docker volumes..."
docker run --rm -v $(pwd)/backups:/backup -v llm-rag-docker_ollama_data:/data alpine tar czf /backup/ollama_data_$TIMESTAMP.tar.gz -C /data . 2>/dev/null || echo "  Ollama volume backup failed"
docker run --rm -v $(pwd)/backups:/backup -v llm-rag-docker_postgres_data:/data alpine tar czf /backup/postgres_data_$TIMESTAMP.tar.gz -C /data . 2>/dev/null || echo "  PostgreSQL volume backup failed"
docker run --rm -v $(pwd)/backups:/backup -v llm-rag-docker_redis_data:/data alpine tar czf /backup/redis_data_$TIMESTAMP.tar.gz -C /data . 2>/dev/null || echo "  Redis volume backup failed"

# Backup database
echo "🗄️  Backing up PostgreSQL database..."
docker-compose exec -T postgres pg_dump -U raguser ragdb > "$BACKUP_DIR/database_dump.sql" 2>/dev/null || echo "  Database backup failed"

# Create system info snapshot
echo "📊 Creating system snapshot..."
cat > "$BACKUP_DIR/system_info.txt" << EOF
Backup Created: $(date)
System: $(uname -a)
Docker Version: $(docker --version)
Docker Compose Version: $(docker-compose --version)

Container Status:
$(docker-compose ps)

Volume Usage:
$(docker system df)
EOF

# Compress backup
echo "🗜️  Compressing backup..."
tar czf "backups/rag_backup_$TIMESTAMP.tar.gz" -C backups "backup_$TIMESTAMP"
rm -rf "$BACKUP_DIR"

# Clean old backups (keep last 10)
echo "🧹 Cleaning old backups..."
ls -t backups/rag_backup_*.tar.gz | tail -n +11 | xargs -r rm

BACKUP_SIZE=$(du -sh "backups/rag_backup_$TIMESTAMP.tar.gz" | cut -f1)
echo "✅ Backup completed: rag_backup_$TIMESTAMP.tar.gz ($BACKUP_SIZE)"