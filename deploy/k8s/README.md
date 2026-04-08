# PM4Py Production Deployment Guide

This guide covers deploying PM4Py to production using Docker Compose (local/single-host) or Kubernetes (cloud/multi-host).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring & Observability](#monitoring--observability)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Docker Compose
- Docker 20.10+
- Docker Compose 2.0+

### Kubernetes
- kubectl 1.25+
- Kubernetes cluster 1.25+ (minikube, kind, or cloud provider)
- (Optional) Helm 3.0+
- (Optional) NGINX Ingress Controller

## Quick Start (Docker Compose)

### 1. Set Environment Variables

Create a `.env` file in the `deploy/` directory:

```bash
cd deploy/
cat > .env << EOF
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_grafana_password_here
EOF
```

### 2. Start All Services

```bash
cd deploy/
docker-compose up -d
```

This starts:
- **PM4Py API** on http://localhost:8000
- **Grafana** on http://localhost:3001
- **Prometheus** on http://localhost:9090
- **Jaeger UI** on http://localhost:16686

### 3. Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Check PM4Py health
curl http://localhost:8000/health

# View logs
docker-compose logs -f pm4py-api
```

### 4. Stop Services

```bash
docker-compose down
# To remove volumes as well
docker-compose down -v
```

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl apply -f deploy/k8s/namespace.yaml
```

### 2. Create Secrets

Edit `deploy/k8s/secret.yaml` with your actual passwords:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pm4py-secret
  namespace: pm4py
type: Opaque
stringData:
  POSTGRES_PASSWORD: "your_secure_password_here"
```

Apply the secret:

```bash
kubectl apply -f deploy/k8s/secret.yaml
```

### 3. Deploy Monitoring Stack

```bash
kubectl apply -f deploy/k8s/monitoring.yaml
```

### 4. Deploy Data Layer

```bash
kubectl apply -f deploy/k8s/postgres-deployment.yaml
kubectl apply -f deploy/k8s/redis-deployment.yaml
```

Wait for PostgreSQL to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=postgres -n pm4py --timeout=60s
```

### 5. Deploy PM4Py API

```bash
kubectl apply -f deploy/k8s/pm4py-deployment.yaml
```

### 6. (Optional) Deploy Ingress

For external access via Ingress:

```bash
kubectl apply -f deploy/k8s/ingress.yaml
```

Then add to your `/etc/hosts`:

```
127.0.0.1 api.pm4py.local
127.0.0.1 grafana.pm4py.local
127.0.0.1 jaeger.pm4py.local
```

### 7. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n pm4py

# Port-forward to access services locally
kubectl port-forward -n pm4py svc/pm4py-api 8000:8000
kubectl port-forward -n pm4py svc/grafana 3000:3000
kubectl port-forward -n pm4py svc/jaeger 16686:16686
```

## Monitoring & Observability

### Grafana Dashboards

Access Grafana at http://localhost:3001 (Docker) or via port-forward (K8s).

Default credentials:
- Username: `admin`
- Password: Check your `.env` file or Secret

### Prometheus Metrics

PM4Py exposes metrics at `/metrics` in Prometheus format:

- `pm4py_discovery_total` - Total process discoveries
- `pm4py_active_discoveries` - Currently active discoveries
- `pm4py_discovery_duration_seconds` - Discovery duration histogram
- `pm4py_events_processed_total` - Total events processed
- `pm4py_fitness_score` - Current fitness score
- `pm4py_precision_score` - Current precision score
- `pm4py_drift_detected_total` - Total drift detections

### Jaeger Tracing

Access Jaeger UI at http://localhost:16686 to view distributed traces.

### Health Checks

PM4Py provides health endpoints:

- `/health` - Liveness probe
- `/ready` - Readiness probe
- `/metrics` - Prometheus metrics

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PM4PY_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `PM4PY_DB_HOST` | PostgreSQL host | postgres |
| `PM4PY_DB_PORT` | PostgreSQL port | 5432 |
| `PM4PY_DB_NAME` | Database name | pm4py |
| `PM4PY_DB_USER` | Database user | pm4py |
| `PM4PY_DB_PASSWORD` | Database password | - |
| `PM4PY_REDIS_HOST` | Redis host | redis |
| `PM4PY_REDIS_PORT` | Redis port | 6379 |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL collector endpoint | http://otel-collector:4317 |
| `OTEL_SERVICE_NAME` | Service name for tracing | pm4py |
| `OTEL_DEPLOYMENT_ENVIRONMENT` | Deployment environment | production |

### Resource Limits

**PM4Py API** (per pod):
- CPU: 100m - 1000m
- Memory: 256Mi - 1Gi

**PostgreSQL**:
- CPU: 100m - 500m
- Memory: 256Mi - 1Gi
- Storage: 10Gi

**Redis**:
- CPU: 50m - 200m
- Memory: 128Mi - 512Mi

## Scaling

### Horizontal Pod Autoscaler

PM4Py API is configured to autoscale:

```yaml
minReplicas: 3
maxReplicas: 10
targetCPUUtilization: 70%
targetMemoryUtilization: 80%
```

Manually scale:

```bash
kubectl scale deployment pm4py-api -n pm4py --replicas=5
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n pm4py
kubectl describe pod <pod-name> -n pm4py
```

### View Logs

```bash
# All pods
kubectl logs -n pm4py -l app=pm4py --tail=100 -f

# Specific pod
kubectl logs -n pm4py <pod-name> --tail=100 -f

# Previous container (if crashed)
kubectl logs -n pm4py <pod-name> --previous
```

### Common Issues

**Pod stuck in Pending state:**
- Check resource requests vs available capacity
- Check if image pull secrets are needed

**CrashLoopBackOff:**
- Check logs for application errors
- Verify environment variables and secrets
- Check database connection

**Failed health checks:**
- Verify `/health` endpoint is responding
- Check initialDelaySeconds and periodSeconds settings

### Database Connection Issues

```bash
# Test PostgreSQL connection from PM4Py pod
kubectl exec -n pm4py <pm4py-pod> -- nc -zv postgres 5432

# View PostgreSQL logs
kubectl logs -n pm4py -l app=postgres
```

## Security Considerations

1. **Change default passwords** in production
2. **Use sealed-secrets** or external secret management (Vault, AWS Secrets Manager)
3. **Enable TLS** for external services
4. **Restrict network access** with NetworkPolicies
5. **Regular security updates** for base images

## Backup & Recovery

### PostgreSQL Backup

```bash
# From within the pod
kubectl exec -n pm4py <postgres-pod> -- pg_dump -U pm4py pm4py > backup.sql

# Restore
kubectl exec -n pm4py -i <postgres-pod> -- psql -U pm4py pm4py < backup.sql
```

### Volume Snapshots

For cloud providers, use volume snapshots:

```bash
# AWS EKS
kubectl create pv snapshot --source=<pvc-name>

# Google GKE
gcloud compute disks snapshot <disk-name>
```

## Support

For issues and questions:
- GitHub: https://github.com/pm4py/pm4py
- Documentation: https://pm4py.fit
