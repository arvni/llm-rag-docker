#!/bin/bash
# Restart RAG System services

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to restart specific service
restart_service() {
    local service_name=$1
    print_status "Restarting $service_name..."
    
    if docker-compose restart "$service_name"; then
        print_success "$service_name restarted successfully"
        
        # Wait for health check
        print_status "Waiting for $service_name to be healthy..."
        local max_attempts=30
        local attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if docker-compose ps "$service_name" | grep -q "healthy\|Up"; then
                print_success "$service_name is healthy"
                return 0
            fi
            
            sleep 2
            ((attempt++))
        done
        
        print_warning "$service_name may not be fully healthy yet"
    else
        print_error "Failed to restart $service_name"
        return 1
    fi
}

# Function to restart all services
restart_all() {
    print_status "Restarting all RAG System services..."
    
    # Create backup before restart
    if [ -f "./scripts/backup.sh" ]; then
        print_status "Creating backup before restart..."
        ./scripts/backup.sh
    fi
    
    # Restart services in order
    local services=("postgres" "redis" "ollama" "rag-app" "nginx" "filebrowser")
    
    for service in "${services[@]}"; do
        if docker-compose ps -q "$service" > /dev/null 2>&1; then
            restart_service "$service"
            sleep 5  # Brief pause between service restarts
        else
            print_warning "Service $service not found or not running"
        fi
    done
    
    # Final status check
    print_status "Checking overall system status..."
    ./scripts/status.sh
}

# Function to perform rolling restart
rolling_restart() {
    print_status "Performing rolling restart..."
    
    # Restart backend services first
    local backend_services=("postgres" "redis")
    for service in "${backend_services[@]}"; do
        restart_service "$service"
        sleep 3
    done
    
    # Restart compute services
    restart_service "ollama"
    sleep 10  # Ollama needs more time to load models
    
    # Restart frontend services
    local frontend_services=("rag-app" "nginx" "filebrowser")
    for service in "${frontend_services[@]}"; do
        restart_service "$service"
        sleep 3
    done
}

# Function to force restart (stop and start)
force_restart() {
    local service_name=$1
    print_warning "Force restarting $service_name..."
    
    docker-compose stop "$service_name"
    sleep 5
    docker-compose start "$service_name"
    
    # Wait for service to be ready
    sleep 10
    
    # Check status
    if docker-compose ps "$service_name" | grep -q "Up"; then
        print_success "$service_name force restarted successfully"
    else
        print_error "Force restart of $service_name may have failed"
    fi
}

# Main script logic
main() {
    local action=${1:-"all"}
    local service_name=${2:-""}
    
    case $action in
        "all")
            restart_all
            ;;
        "rolling")
            rolling_restart
            ;;
        "service")
            if [ -z "$service_name" ]; then
                print_error "Service name required for service restart"
                echo "Usage: $0 service <service_name>"
                exit 1
            fi
            restart_service "$service_name"
            ;;
        "force")
            if [ -z "$service_name" ]; then
                print_error "Service name required for force restart"
                echo "Usage: $0 force <service_name>"
                exit 1
            fi
            force_restart "$service_name"
            ;;
        "help"|"-h"|"--help")
            echo "RAG System Restart Script"
            echo "========================="
            echo ""
            echo "Usage: $0 [action] [service_name]"
            echo ""
            echo "Actions:"
            echo "  all      - Restart all services (default)"
            echo "  rolling  - Rolling restart (minimal downtime)"
            echo "  service  - Restart specific service"
            echo "  force    - Force restart (stop then start)"
            echo "  help     - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Restart all services"
            echo "  $0 rolling           # Rolling restart"
            echo "  $0 service ollama    # Restart only Ollama"
            echo "  $0 force rag-app     # Force restart RAG app"
            echo ""
            echo "Available services:"
            echo "  ollama, rag-app, postgres, redis, nginx, filebrowser"
            ;;
        *)
            print_error "Unknown action: $action"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run from the project root directory."
    exit 1
fi

# Run main function
main "$@"

print_success "Restart operation completed!"
echo ""
echo "🌐 Access Points:"
echo "  • RAG Application: http://localhost:8501"
echo "  • File Manager: http://localhost:8080"  
echo "  • System Status: ./scripts/status.sh"