.PHONY: help install start stop status update backup logs clean dev prod monitoring

# Default target
help:
	@echo "RAG System Management Commands"
	@echo "=============================="
	@echo "install     - Install and setup the system"
	@echo "start       - Start all services"
	@echo "stop        - Stop all services"  
	@echo "restart     - Restart all services"
	@echo "status      - Check system status"
	@echo "update      - Update system"
	@echo "backup      - Create system backup"
	@echo "logs        - View system logs"
	@echo "clean       - Clean up system"
	@echo "dev         - Start development environment"
	@echo "prod        - Start production environment"
	@echo "monitoring  - Start monitoring stack"
	@echo "models      - Install LLM models"
	@echo "health      - Health check"

install:
	./scripts/start.sh

start:
	docker-compose up -d

stop:
	docker-compose down

restart:
	docker-compose restart

status:
	./scripts/status.sh

update:
	./scripts/update.sh

backup:
	./scripts/backup.sh

logs:
	./scripts/logs.sh

clean:
	docker-compose down -v
	docker system prune -af

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

monitoring:
	docker-compose -f docker-compose.yml -f monitoring/docker-compose.monitoring.yml up -d

models:
	./scripts/install-models.sh

health:
	./scripts/health-check.sh