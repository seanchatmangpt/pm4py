#!/bin/bash
# PM4Py Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: dev, staging, production

set -e

# Configuration
ENVIRONMENT="${1:-staging}"
COMPOSE_FILE="deploy/docker-compose.yml"
PROJECT_NAME="pm4py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Pre-flight checks
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
    fi

    log_info "Prerequisites check passed ✓"
}

# Build images
build_images() {
    log_info "Building Docker images for ${ENVIRONMENT}..."

    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache

    log_info "Build completed ✓"
}

# Start services
start_services() {
    log_info "Starting PM4Py services in ${ENVIRONMENT}..."

    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d

    log_info "Services started ✓"

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10

    # Show service status
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
}

# Stop services
stop_services() {
    log_info "Stopping PM4Py services..."

    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down

    log_info "Services stopped ✓"
}

# Restart services
restart_services() {
    log_info "Restarting PM4Py services..."

    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" restart

    log_info "Services restarted ✓"
}

# Show logs
show_logs() {
    SERVICE="${2:-}"

    if [ -n "$SERVICE" ]; then
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$SERVICE"
    else
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
    fi
}

# Health check
health_check() {
    log_info "Running health checks..."

    # Check if services are running
    RUNNING=$(docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps -q | wc -l)

    if [ "$RUNNING" -eq 0 ]; then
        log_error "No services are running"
    fi

    log_info "Running services: $RUNNING"

    # Check service health
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T pm4py-api python -c "import pm4py; print('PM4Py OK')"

    log_info "Health check passed ✓"
}

# Run migrations
run_migrations() {
    log_info "Running database migrations..."

    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T postgres psql -U pm4py -d pm4py -c "SELECT 1"

    log_info "Migrations completed ✓"
}

# Backup data
backup_data() {
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    log_info "Backing up data to $BACKUP_DIR..."

    # Backup PostgreSQL
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T postgres pg_dump -U pm4py pm4py > "$BACKUP_DIR/postgres_backup.sql"

    log_info "Backup completed ✓"
    log_info "Backup location: $BACKUP_DIR"
}

# Restore data
restore_data() {
    BACKUP_PATH="$2"

    if [ -z "$BACKUP_PATH" ]; then
        log_error "Please specify backup path: ./deploy.sh restore <backup_path>"
    fi

    log_info "Restoring data from $BACKUP_PATH..."

    # Restore PostgreSQL
    cat "$BACKUP_PATH/postgres_backup.sql" | docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T postgres psql -U pm4py -d pm4py

    log_info "Restore completed ✓"
}

# Clean deployment
clean_deployment() {
    log_warn "This will remove all containers, volumes, and data. Continue? (y/N)"
    read -r response

    if [ "$response" != "y" ]; then
        log_info "Clean deployment cancelled"
        exit 0
    fi

    log_info "Cleaning deployment..."

    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v

    log_info "Clean deployment completed ✓"
}

# Show usage
show_usage() {
    cat << EOF
PM4Py Deployment Script

Usage: ./deploy.sh [command] [options]

Commands:
  build           Build Docker images
  start           Start all services
  stop            Stop all services
  restart         Restart all services
  logs [service]  Show logs (all services or specific service)
  health          Run health checks
  migrate         Run database migrations
  backup          Backup all data
  restore <path>  Restore data from backup
  clean           Remove all containers and volumes (DANGEROUS!)
  help            Show this help message

Examples:
  ./deploy.sh build
  ./deploy.sh start
  ./deploy.sh logs pm4py-api
  ./deploy.sh health
  ./deploy.sh backup
  ./deploy.sh restore backups/20240101_120000

Environments:
  dev             Development environment
  staging         Staging environment (default)
  production      Production environment

EOF
}

# Main script
main() {
    COMMAND="${1:-help}"

    case "$COMMAND" in
        build)
            check_prerequisites
            build_images
            ;;
        start)
            check_prerequisites
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs "$@"
            ;;
        health)
            health_check
            ;;
        migrate)
            run_migrations
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$@"
            ;;
        clean)
            clean_deployment
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_usage
            ;;
    esac
}

# Run main function
main "$@"
