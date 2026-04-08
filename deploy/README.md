# PM4Py Production Deployment

This directory contains production-ready deployment configurations for PM4Py.

## Quick Start

### Docker Compose (Recommended for local/single-host)

```bash
# Create environment file
cat > .env << EOF
POSTGRES_PASSWORD=your_secure_password
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_grafana_password
EOF

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f pm4py-api
```

### Kubernetes (Recommended for production/cloud)

```bash
# Deploy to Kubernetes
cd k8s/
make install

# Check status
make status

# Port-forward for local access
make port-forward
```

See `k8s/README.md` for detailed Kubernetes deployment instructions.

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  PM4Py API   │──────│ OTEL Collector│──────│   Jaeger    │
│  :8000      │      │  :4317/:4318  │      │  :16686     │
└─────────────┘      └──────────────┘      └─────────────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐
│ PostgreSQL  │ │  Redis    │ │  Prometheus│
│  :5432     │ │  :6379    │ │  :9090     │
└─────────────┘ └───────────┘ └────────────┘
                                           │
                                    ┌───────▼─────┐
                                    │   Grafana   │
                                    │  :3001      │
                                    └─────────────┘
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| PM4Py API | 8000 | Main PM4Py service |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| OTEL Collector | 4317/4318 | Telemetry collector |
| Jaeger | 16686 | Distributed tracing UI |
| Prometheus | 9090 | Metrics collector |
| Grafana | 3001 | Monitoring dashboard |

## Deployment Commands

### Build Images

```bash
./deploy.sh build
```

### Start Services

```bash
./deploy.sh start
```

### Stop Services

```bash
./deploy.sh stop
```

### Restart Services

```bash
./deploy.sh restart
```

### View Logs

```bash
# All logs
./deploy.sh logs

# Specific service
./deploy.sh logs pm4py-api
```

### Health Check

```bash
./deploy.sh health
```

### Backup Data

```bash
./deploy.sh backup
```

### Restore Data

```bash
./deploy.sh restore backups/20240101_120000
```

### Clean Deployment

```bash
# Removes all containers, volumes, and data
./deploy.sh clean
```

## Docker Compose

```bash
# Start specific services
docker compose -f deploy/docker-compose.yml up -d pm4py-api postgres redis

# Scale PM4Py API
docker compose -f deploy/docker-compose.yml up -d --scale pm4py-api=3
```

## Configuration

### Environment Variables

Set environment variables before starting:

```bash
export POSTGRES_PASSWORD=your_secure_password
export GRAFANA_USER=admin
export GRAFANA_PASSWORD=your_secure_password
./deploy.sh start
```

### Resource Limits

Edit `docker-compose.yml` to add resource limits:

```yaml
services:
  pm4py-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## CI/CD

The `.github/workflows/ci.yml` file contains the CI/CD pipeline:

1. **Test**: Run tests across Python 3.9-3.14
2. **Lint**: Run ruff and mypy
3. **Build**: Build and push Docker images
4. **Security**: Run Trivy vulnerability scanner
5. **Deploy**: Deploy on release

## Monitoring

Access monitoring dashboards:

- **Grafana**: http://localhost:3001 (admin/admin)
- **Jaeger**: http://localhost:16686
- **Prometheus**: http://localhost:9090

## Production Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Configure SSL/TLS certificates
- [ ] Set up backup strategy
- [ ] Configure log aggregation
- [ ] Set up alerting (Slack, PagerDuty)
- [ ] Review resource limits
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Set up monitoring dashboards
- [ ] Test disaster recovery procedure

## Troubleshooting

### Services won't start

```bash
# Check logs
./deploy.sh logs

# Check container status
docker compose -f deploy/docker-compose.yml ps

# Check resource usage
docker stats
```

### Database connection issues

```bash
# Check PostgreSQL
docker compose -f deploy/docker-compose.yml exec postgres psql -U pm4py -d pm4py

# Reset database
./deploy.sh clean
./deploy.sh start
```

### High memory usage

```bash
# Clean up Docker resources
docker system prune -a

# Restart services
./deploy.sh restart
```
