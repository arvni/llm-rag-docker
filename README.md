# 🤖 Advanced RAG System with Docker

A comprehensive, production-ready RAG (Retrieval-Augmented Generation) system powered by local LLMs, designed for document Q&A with advanced features.

## 🌟 Features

### Core Capabilities
- **🤖 Local LLM Integration**: Ollama with GPU acceleration
- **📄 Advanced Document Processing**: PDF, DOCX, TXT, Images with OCR
- **🔍 Intelligent Search**: Vector similarity search with ChromaDB
- **💬 Interactive Chat**: Streamlit-based web interface
- **🔧 Model Management**: Easy installation and switching between models

### Advanced Features
- **📊 Comprehensive Monitoring**: Prometheus, Grafana, ELK Stack
- **🐳 Full Containerization**: Docker Compose orchestration
- **🔄 Auto-scaling**: Resource management and optimization
- **💾 Data Persistence**: PostgreSQL, Redis caching
- **🔒 Security**: Nginx reverse proxy, SSL support
- **📈 Performance Metrics**: GPU utilization, system health
- **🛠️ Management Tools**: Automated backup, updates, health checks

## 🚀 Quick Start

### Prerequisites
- **OS**: Pop!_OS 22.04 LTS (or Ubuntu 22.04+)
- **GPU**: NVIDIA RTX 3080 (or compatible)
- **RAM**: 16GB+ recommended
- **Storage**: 100GB+ available space
- **Docker**: 24.0+ with Compose V2
- **NVIDIA Container Toolkit**: Latest version

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd llm-rag-docker

# Make scripts executable
chmod +x scripts/*.sh

# Start the system
./scripts/start.sh

# Wait for services to initialize (2-3 minutes)
# Access the application at http://localhost:8501
```

## 📁 Directory Structure

```
llm-rag-docker/
├── app/                    # Main application
│   ├── components/         # Modular components
│   ├── utils/             # Utility functions
│   ├── static/            # CSS and assets
│   └── Dockerfile         # App container
├── config/                # Configuration files
│   ├── nginx/             # Reverse proxy config
│   ├── prometheus/        # Metrics config
│   └── grafana/          # Dashboard config
├── scripts/               # Management scripts
├── monitoring/            # Monitoring stack
├── data/                  # Persistent data
├── uploads/               # Document uploads
├── models/                # LLM models
└── backups/              # System backups
```

## 🛠️ Management Commands

```bash
# System Management
./scripts/start.sh         # Start all services
./scripts/stop.sh          # Stop all services
./scripts/status.sh        # Check system status
./scripts/update.sh        # Update system
./scripts/restart.sh       # Restart services

# Monitoring & Maintenance
./scripts/logs.sh [service]    # View logs
./scripts/backup.sh           # Create backup
./scripts/health-check.sh     # Health check
./scripts/install-models.sh   # Install LLM models

# Development
docker-compose -f docker-compose.dev.yml up  # Dev environment
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **RAG App** | http://localhost:8501 | Main application |
| **File Manager** | http://localhost:8080 | Upload management |
| **Grafana** | http://localhost:3000 | Monitoring dashboards |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Kibana** | http://localhost:5601 | Log analysis |
| **Ollama API** | http://localhost:11434 | LLM API |

## 📊 System Requirements

### Minimum Configuration
- **CPU**: 4+ cores
- **RAM**: 16GB
- **GPU**: 6GB+ VRAM
- **Storage**: 50GB SSD

### Recommended Configuration  
- **CPU**: 8+ cores (Intel i7/AMD Ryzen 7)
- **RAM**: 32GB+
- **GPU**: RTX 3080/4080 (10GB+ VRAM)
- **Storage**: 200GB+ NVMe SSD

### Model Performance (RTX 3080)
- **7B models**: 40+ tokens/sec
- **13B models**: 20+ tokens/sec  
- **70B models**: Limited (requires quantization)

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and customize:

```bash
# Core settings
OLLAMA_NUM_PARALLEL=4
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
LOG_LEVEL=INFO

# GPU settings
NVIDIA_VISIBLE_DEVICES=all
CUDA_VISIBLE_DEVICES=0

# Database settings
POSTGRES_PASSWORD=your-secure-password
```

### Model Installation
```bash
# Install recommended models
./scripts/install-models.sh

# Or manually via Docker
docker-compose exec ollama ollama pull llama3.1:8b
docker-compose exec ollama ollama pull mistral:7b
```

## 📈 Monitoring

The system includes comprehensive monitoring:

- **System Metrics**: CPU, RAM, GPU utilization
- **Application Metrics**: Response times, error rates
- **Log Aggregation**: Centralized logging with ELK
- **Alerting**: Automated notifications for issues
- **Health Checks**: Continuous service monitoring

Access Grafana at http://localhost:3000 (admin/admin123)

## 🔒 Security Features

- **Reverse Proxy**: Nginx with SSL termination
- **Container Security**: Non-root user execution
- **Network Isolation**: Internal Docker networks
- **Access Control**: Service-level authentication
- **Data Encryption**: SSL/TLS for external connections

## 🚨 Troubleshooting

### Common Issues

**GPU Not Detected:**
```bash
# Check NVIDIA driver
nvidia-smi

# Test Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**Services Not Starting:**
```bash
# Check system status
./scripts/status.sh

# View service logs
./scripts/logs.sh [service-name]

# Health check
./scripts/health-check.sh
```

**High Memory Usage:**
```bash
# Monitor resources
docker stats

# Restart services
./scripts/restart.sh
```

### Performance Optimization

1. **GPU Memory**: Adjust `OLLAMA_MAX_LOADED_MODELS`
2. **CPU Cores**: Set Docker CPU limits
3. **Cache Settings**: Configure Redis parameters
4. **Model Selection**: Use appropriate model sizes

## 📝 Usage Guide

1. **Start System**: `./scripts/start.sh`
2. **Upload Documents**: Use web interface or file manager
3. **Process Documents**: Click "Process Documents" in sidebar
4. **Ask Questions**: Type questions in chat interface
5. **Monitor Performance**: Check Grafana dashboards
6. **Manage Models**: Use model management interface

## 🔄 Updates & Maintenance

```bash
# Regular maintenance
./scripts/backup.sh      # Weekly backups
./scripts/update.sh      # Monthly updates
./scripts/health-check.sh # Daily health checks

# Log rotation
docker system prune -f   # Clean unused images
```

## 🐛 Issues & Support

- **Health Check**: `./scripts/health-check.sh`
- **Logs**: `./scripts/logs.sh`
- **System Status**: `./scripts/status.sh`
- **GitHub Issues**: [Repository Issues](https://github.com/your-repo/issues)

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 🙏 Acknowledgments

- **Ollama**: Local LLM inference
- **LangChain**: RAG framework
- **Streamlit**: Web interface
- **ChromaDB**: Vector database
- **Docker**: Containerization platform

---

**🚀 Built for Production • 🔒 Security First • 📈 Performance Optimized**