#!/bin/bash
# Main startup script

set -e

echo "🚀 Starting Advanced RAG System..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        exit 1
    fi
    
    # Check NVIDIA runtime
    if ! docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu20.04 nvidia-smi > /dev/null 2>&1; then
        print_error "NVIDIA Docker runtime not available!"
        print_warning "GPU acceleration will not work"
    else
        print_success "NVIDIA Docker runtime detected"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating directories..."
    
    directories=(
        "data/ollama"
        "data/chroma_db"
        "data/embeddings"
        "data/cache"
        "uploads"
        "models"
        "backups"
        "logs"
        "config/ssl"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_status "Created directory: $dir"
    done
}

# Set permissions
set_permissions() {
    print_status "Setting permissions..."
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    # Set data directory permissions
    chown -R $USER:$USER data/ uploads/ logs/ backups/ 2>/dev/null || true
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Pull latest images
    print_status "Pulling latest images..."
    docker compose pull
    
    # Build and start services
    print_status "Building and starting containers..."
    docker compose up --build -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check service status
    print_status "Checking service status..."
    docker compose ps
}

# Install default models
install_models() {
    print_status "Installing default models..."
    
    # Wait for Ollama to be ready
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker compose exec -T ollama ollama list > /dev/null 2>&1; then
            print_success "Ollama is ready"
            break
        fi
        
        print_status "Waiting for Ollama... ($((attempt + 1))/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Ollama failed to start within timeout"
        return 1
    fi
    
    # Install default model
    print_status "Installing Llama 3.1 8B model..."
    docker compose exec -T ollama ollama pull llama3.1:8b
    
    print_status "Installing Mistral 7B model..."
    docker compose exec -T ollama ollama pull mistral:7b
}

# Display access information
show_access_info() {
    print_success "🎉 RAG System started successfully!"
    echo ""
    echo "📡 Access Points:"
    echo "  🌐 Main Application: http://localhost:8501"
    echo "  📁 File Manager: http://localhost:8080 (admin/admin)"
    echo "  🔧 Nginx Proxy: http://localhost:80"
    echo "  🤖 Ollama API: http://localhost:11434"
    echo "  📊 Redis: localhost:6379"
    echo "  🗄️  PostgreSQL: localhost:5432"
    echo ""
    echo "🛠️  Management Commands:"
    echo "  📊 Check Status: ./scripts/status.sh"
    echo "  🛑 Stop System: ./scripts/stop.sh"
    echo "  🔄 Update System: ./scripts/update.sh"
    echo "  💾 Backup Data: ./scripts/backup.sh"
    echo "  📝 View Logs: ./scripts/logs.sh"
    echo ""
    echo "📚 Documentation: README.md"
}

# Main execution
main() {
    check_prerequisites
    create_directories
    set_permissions
    start_services
    install_models
    show_access_info
}

# Run main function
main