#!/bin/bash
# scripts/status.sh - Comprehensive RAG System Status Check

set -e

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Unicode symbols for better visual representation
CHECK_MARK="✅"
CROSS_MARK="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
GEAR="⚙️"
CHART="📊"
DATABASE="🗄️"
NETWORK="🌐"
GPU="🎮"
CPU="💻"
MEMORY="🧠"
DISK="💾"

# Function to print colored status
print_header() {
    echo -e "\n${WHITE}$1${NC}"
    echo -e "${WHITE}$(printf '=%.0s' {1..60})${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK_MARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

print_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

print_metric() {
    local label=$1
    local value=$2
    local unit=$3
    local threshold=${4:-""}
    
    if [[ -n $threshold ]]; then
        if (( $(echo "$value > $threshold" | bc -l) )); then
            echo -e "${RED}  $label: $value$unit${NC}"
        else
            echo -e "${GREEN}  $label: $value$unit${NC}"
        fi
    else
        echo -e "${CYAN}  $label: $value$unit${NC}"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get container status
get_container_status() {
    local container_name=$1
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name"; then
        local status=$(docker ps --format "{{.Status}}" --filter "name=$container_name")
        if [[ $status == *"healthy"* ]]; then
            echo "healthy"
        elif [[ $status == *"Up"* ]]; then
            echo "running"
        else
            echo "unhealthy"
        fi
    else
        echo "stopped"
    fi
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local url=$2
    local timeout=${3:-5}
    
    if curl -f -m $timeout "$url" >/dev/null 2>&1; then
        print_success "$service_name: Healthy"
        return 0
    else
        print_error "$service_name: Unhealthy"
        return 1
    fi
}

# Function to get system metrics
get_system_metrics() {
    # CPU Usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    
    # Memory Usage
    local mem_info=$(free | grep Mem)
    local mem_total=$(echo $mem_info | awk '{print $2}')
    local mem_used=$(echo $mem_info | awk '{print $3}')
    local mem_percent=$(echo "scale=1; $mem_used * 100 / $mem_total" | bc)
    
    # Disk Usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    echo "$cpu_usage,$mem_percent,$disk_usage"
}

# Function to get GPU metrics
get_gpu_metrics() {
    if command_exists nvidia-smi; then
        # GPU utilization
        local gpu_util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1)
        
        # GPU memory
        local gpu_mem_used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
        local gpu_mem_total=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        local gpu_mem_percent=$(echo "scale=1; $gpu_mem_used * 100 / $gpu_mem_total" | bc)
        
        # GPU temperature
        local gpu_temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | head -1)
        
        echo "$gpu_util,$gpu_mem_percent,$gpu_temp,$gpu_mem_used,$gpu_mem_total"
    else
        echo "N/A,N/A,N/A,N/A,N/A"
    fi
}

# Function to get Docker stats
get_docker_stats() {
    if command_exists docker; then
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" 2>/dev/null
    fi
}

# Function to check network connectivity
check_network() {
    local endpoints=(
        "ollama:http://localhost:11434/api/tags"
        "rag-app:http://localhost:8501/_stcore/health"
        "filebrowser:http://localhost:8080"
        "nginx:http://localhost:80/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        IFS=':' read -r name url <<< "$endpoint"
        check_service_health "$name" "$url"
    done
}

# Function to check database connections
check_databases() {
    # PostgreSQL
    if docker exec postgres pg_isready -U raguser -d ragdb >/dev/null 2>&1; then
        print_success "PostgreSQL: Connected"
    else
        print_error "PostgreSQL: Connection failed"
    fi
    
    # Redis
    if docker exec redis redis-cli ping >/dev/null 2>&1; then
        print_success "Redis: Connected"
    else
        print_error "Redis: Connection failed"
    fi
}

# Function to show model information
show_model_info() {
    print_header "${ROCKET} Ollama Models"
    
    if docker exec ollama ollama list >/dev/null 2>&1; then
        echo -e "${CYAN}Available Models:${NC}"
        docker exec ollama ollama list | tail -n +2 | while read -r line; do
            local model_name=$(echo "$line" | awk '{print $1}')
            local model_size=$(echo "$line" | awk '{print $2}')
            local modified=$(echo "$line" | awk '{print $3, $4}')
            echo -e "${GREEN}  • ${model_name}${NC} (${model_size}) - Modified: ${modified}"
        done
        
        # Show running models
        echo -e "\n${CYAN}Running Models:${NC}"
        if docker exec ollama ollama ps >/dev/null 2>&1; then
            docker exec ollama ollama ps | tail -n +2 | while read -r line; do
                if [[ -n "$line" ]]; then
                    local model_name=$(echo "$line" | awk '{print $1}')
                    local size=$(echo "$line" | awk '{print $2}')
                    local processor=$(echo "$line" | awk '{print $3}')
                    echo -e "${GREEN}  • ${model_name}${NC} (${size}) - ${processor}"
                fi
            done
        else
            echo -e "${YELLOW}  No models currently running${NC}"
        fi
    else
        print_error "Cannot connect to Ollama service"
    fi
}

# Function to show storage usage
show_storage_info() {
    print_header "${DISK} Storage Information"
    
    # Docker volumes
    echo -e "${CYAN}Docker Volumes:${NC}"
    docker volume ls --format "table {{.Driver}}\t{{.Name}}" | grep -E "(ollama|postgres|redis)" | while read -r line; do
        local volume_name=$(echo "$line" | awk '{print $2}')
        if [[ -n "$volume_name" ]]; then
            echo -e "${GREEN}  • $volume_name${NC}"
        fi
    done
    
    echo -e "\n${CYAN}Directory Sizes:${NC}"
    local dirs=("data" "uploads" "logs" "backups" "models")
    
    for dir in "${dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            local size=$(du -sh "$dir" 2>/dev/null | cut -f1)
            echo -e "${GREEN}  • $dir: $size${NC}"
        else
            echo -e "${YELLOW}  • $dir: Not found${NC}"
        fi
    done
}

# Function to show recent logs
show_recent_activity() {
    print_header "${INFO} Recent Activity"
    
    echo -e "${CYAN}Recent Container Events:${NC}"
    docker events --since="5m" --until="now" --format "{{.Time}} {{.Action}} {{.Actor.Attributes.name}}" 2>/dev/null | tail -5 | while read -r line; do
        if [[ -n "$line" ]]; then
            echo -e "${GREEN}  • $line${NC}"
        fi
    done
    
    echo -e "\n${CYAN}Recent Error Logs:${NC}"
    if [[ -d "logs" ]]; then
        find logs -name "*.log" -type f -exec grep -l "ERROR\|FATAL\|Exception" {} \; | head -3 | while read -r logfile; do
            echo -e "${RED}  • Errors in: $logfile${NC}"
            tail -2 "$logfile" 2>/dev/null | sed 's/^/    /'
        done
    else
        echo -e "${GREEN}  • No error logs found${NC}"
    fi
}

# Function to check system health score
calculate_health_score() {
    local score=100
    local issues=0
    
    # Check container health
    local containers=("ollama" "rag-app" "postgres" "redis" "nginx" "filebrowser")
    for container in "${containers[@]}"; do
        local status=$(get_container_status "$container")
        if [[ "$status" != "healthy" && "$status" != "running" ]]; then
            ((score -= 15)) 
            ((issues++))
        fi
    done
    
    # Check system resources
    IFS=',' read -r cpu_usage mem_usage disk_usage <<< "$(get_system_metrics)"
    
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        ((score -= 10))
        ((issues++))
    fi
    
    if (( $(echo "$mem_usage > 85" | bc -l) )); then
        ((score -= 10))
        ((issues++))
    fi
    
    if (( disk_usage > 90 )); then
        ((score -= 15))
        ((issues++))
    fi
    
    # Ensure score doesn't go below 0
    if (( score < 0 )); then
        score=0
    fi
    
    echo "$score,$issues"
}

# Main status display function
main() {
    clear
    
    echo -e "${WHITE}"
    echo "██████╗  █████╗  ██████╗     ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗"
    echo "██╔══██╗██╔══██╗██╔════╝     ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║"
    echo "██████╔╝███████║██║  ███╗    ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║"
    echo "██╔══██╗██╔══██║██║   ██║    ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║"
    echo "██║  ██║██║  ██║╚██████╔╝    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║"
    echo "╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝     ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝"
    echo -e "${NC}\n"
    
    # Calculate overall health
    IFS=',' read -r health_score issues_count <<< "$(calculate_health_score)"
    
    if (( health_score >= 90 )); then
        echo -e "${GREEN}${CHECK_MARK} System Health: EXCELLENT ($health_score/100)${NC}"
    elif (( health_score >= 70 )); then
        echo -e "${YELLOW}${WARNING} System Health: GOOD ($health_score/100) - $issues_count issues${NC}"
    elif (( health_score >= 50 )); then
        echo -e "${YELLOW}${WARNING} System Health: FAIR ($health_score/100) - $issues_count issues${NC}"
    else
        echo -e "${RED}${CROSS_MARK} System Health: POOR ($health_score/100) - $issues_count issues${NC}"
    fi
    
    echo -e "${CYAN}Generated: $(date)${NC}\n"
    
    # Container Status
    print_header "${GEAR} Container Status"
    
    local containers=("ollama" "rag-app" "postgres" "redis" "nginx" "filebrowser")
    for container in "${containers[@]}"; do
        local status=$(get_container_status "$container")
        case $status in
            "healthy")
                print_success "$container: Healthy"
                ;;
            "running") 
                print_info "$container: Running"
                ;;
            "unhealthy")
                print_warning "$container: Unhealthy"
                ;;
            "stopped")
                print_error "$container: Stopped"
                ;;
        esac
    done
    
    # System Resources
    print_header "${CPU} System Resources"
    
    IFS=',' read -r cpu_usage mem_usage disk_usage <<< "$(get_system_metrics)"
    
    print_metric "CPU Usage" "$cpu_usage" "%" "80"
    print_metric "Memory Usage" "$mem_usage" "%" "85"
    print_metric "Disk Usage" "$disk_usage" "%" "90"
    
    # GPU Information
    if command_exists nvidia-smi; then
        print_header "${GPU} GPU Status"
        
        IFS=',' read -r gpu_util gpu_mem_percent gpu_temp gpu_mem_used gpu_mem_total <<< "$(get_gpu_metrics)"
        
        print_metric "GPU Utilization" "$gpu_util" "%" "95"
        print_metric "GPU Memory" "$gpu_mem_percent" "%" "90"
        print_metric "GPU Temperature" "$gpu_temp" "°C" "80"
        print_metric "VRAM Used" "$gpu_mem_used" "MB"
        print_metric "VRAM Total" "$gpu_mem_total" "MB"
        
        echo -e "\n${CYAN}GPU Details:${NC}"
        nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader | while read -r gpu_info; do
            echo -e "${GREEN}  • $gpu_info${NC}"
        done
    else
        print_header "${GPU} GPU Status"
        print_warning "NVIDIA drivers not available"
    fi
    
    # Network Connectivity
    print_header "${NETWORK} Network Status"
    check_network
    
    # Database Status  
    print_header "${DATABASE} Database Status"
    check_databases
    
    # Model Information
    show_model_info
    
    # Storage Information
    show_storage_info
    
    # Docker Resource Usage
    print_header "${CHART} Resource Usage by Container"
    echo -e "${CYAN}Container Resource Usage:${NC}"
    get_docker_stats | tail -n +2 | while read -r line; do
        if [[ -n "$line" ]]; then
            echo -e "${GREEN}  $line${NC}"
        fi
    done
    
    # Recent Activity
    show_recent_activity
    
    # Quick Actions
    print_header "${ROCKET} Quick Actions"
    echo -e "${CYAN}Management Commands:${NC}"
    echo -e "${GREEN}  • Restart System: ./scripts/restart.sh${NC}"
    echo -e "${GREEN}  • View Logs: ./scripts/logs.sh${NC}"
    echo -e "${GREEN}  • Backup Data: ./scripts/backup.sh${NC}"
    echo -e "${GREEN}  • Update System: ./scripts/update.sh${NC}"
    echo -e "${GREEN}  • Health Check: ./scripts/health-check.sh${NC}"
    
    echo -e "\n${CYAN}Access Points:${NC}"
    echo -e "${GREEN}  • RAG Application: http://localhost:8501${NC}"
    echo -e "${GREEN}  • File Manager: http://localhost:8080${NC}"
    echo -e "${GREEN}  • System Proxy: http://localhost:80${NC}"
    
    # Footer
    echo -e "\n${WHITE}$(printf '=%.0s' {1..60})${NC}"
    echo -e "${BLUE}${INFO} Run './scripts/status.sh --help' for more options${NC}"
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "RAG System Status Script"
        echo "======================="
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --json         Output status in JSON format"
        echo "  --brief        Show brief status only"
        echo "  --watch        Continuously monitor (refresh every 5s)"
        echo ""
        ;;
    "--json")
        # JSON output for API integration
        health_score=$(calculate_health_score | cut -d',' -f1)
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"health_score\": $health_score,"
        echo "  \"containers\": {"
        for container in ollama rag-app postgres redis nginx filebrowser; do
            status=$(get_container_status "$container")
            echo "    \"$container\": \"$status\","
        done | sed '$ s/,$//'
        echo "  },"
        IFS=',' read -r cpu mem disk <<< "$(get_system_metrics)"
        echo "  \"system\": {"
        echo "    \"cpu_usage\": $cpu,"
        echo "    \"memory_usage\": $mem,"
        echo "    \"disk_usage\": $disk"
        echo "  }"
        echo "}"
        ;;
    "--brief")
        # Brief status for quick checks
        IFS=',' read -r health_score issues_count <<< "$(calculate_health_score)"
        echo "RAG System Status: $health_score/100 ($issues_count issues)"
        
        for container in ollama rag-app postgres redis; do
            status=$(get_container_status "$container")
            echo "$container: $status"
        done
        ;;
    "--watch")
        # Continuous monitoring
        while true; do
            main
            echo -e "\n${YELLOW}Refreshing in 5 seconds... (Ctrl+C to exit)${NC}"
            sleep 5
        done
        ;;
    *)
        # Default full status
        main
        ;;
esac