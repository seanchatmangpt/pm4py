# PM4Py Kubernetes Deployment Makefile

# Variables
NAMESPACE := pm4py
KUBECTL := kubectl
K8S_DIR := deploy/k8s

.PHONY: help install uninstall status logs port-forward clean

# Default target
help:
	@echo "PM4Py Kubernetes Deployment"
	@echo ""
	@echo "Targets:"
	@echo "  make install         - Deploy all PM4Py components to Kubernetes"
	@echo "  make uninstall       - Remove all PM4Py components from Kubernetes"
	@echo "  make status          - Show status of all PM4Py pods"
	@echo "  make logs            - Show logs from PM4Py API"
	@echo "  make port-forward    - Port-forward services to localhost"
	@echo "  make clean           - Remove all resources including PVCs"
	@echo "  make restart         - Restart PM4Py API deployment"
	@echo "  make scale N=5       - Scale PM4Py API to N replicas"

# Install all components
install: install-namespace install-secrets install-monitoring install-data-layer install-api install-ingress
	@echo "Waiting for pods to be ready..."
	$(KUBECTL) wait --for=condition=ready pod -l app=pm4py -n $(NAMESPACE) --timeout=120s || true
	@echo "Installation complete!"
	@$(MAKE) status

# Uninstall all components
uninstall:
	$(KUBECTL) delete -f $(K8S_DIR)/ingress.yaml --ignore-not-found=true
	$(KUBECTL) delete -f $(K8S_DIR)/pm4py-deployment.yaml --ignore-not-found=true
	$(KUBECTL) delete -f $(K8S_DIR)/postgres-deployment.yaml --ignore-not-found=true
	$(KUBECTL) delete -f $(K8S_DIR)/redis-deployment.yaml --ignore-not-found=true
	$(KUBECTL) delete -f $(K8S_DIR)/monitoring.yaml --ignore-not-found=true
	$(KUBECTL) delete -f $(K8S_DIR)/configmap.yaml --ignore-not-found=true
	$(KUBECTL) delete -f $(K8S_DIR)/secret.yaml --ignore-not-found=true
	$(KUBECTL) delete -f $(K8S_DIR)/namespace.yaml --ignore-not-found=true
	@echo "Uninstall complete!"

# Install namespace
install-namespace:
	$(KUBECTL) apply -f $(K8S_DIR)/namespace.yaml

# Install secrets (edit first!)
install-secrets:
	@echo "WARNING: Make sure to edit deploy/k8s/secret.yaml with actual passwords first!"
	$(KUBECTL) apply -f $(K8S_DIR)/secret.yaml

# Install monitoring stack
install-monitoring:
	$(KUBECTL) apply -f $(K8S_DIR)/monitoring.yaml
	@echo "Waiting for monitoring stack..."
	sleep 10

# Install data layer
install-data-layer:
	$(KUBECTL) apply -f $(K8S_DIR)/postgres-deployment.yaml
	$(KUBECTL) apply -f $(K8S_DIR)/redis-deployment.yaml
	@echo "Waiting for data layer..."
	$(KUBECTL) wait --for=condition=ready pod -l app=postgres -n $(NAMESPACE) --timeout=60s

# Install API
install-api:
	$(KUBECTL) apply -f $(K8S_DIR)/configmap.yaml
	$(KUBECTL) apply -f $(K8S_DIR)/pm4py-deployment.yaml

# Install ingress
install-ingress:
	$(KUBECTL) apply -f $(K8S_DIR)/ingress.yaml

# Show status
status:
	@echo "=== PM4Py Pods ==="
	$(KUBECTL) get pods -n $(NAMESPACE)
	@echo ""
	@echo "=== PM4Py Services ==="
	$(KUBECTL) get svc -n $(NAMESPACE)
	@echo ""
	@echo "=== PM4Py Deployments ==="
	$(KUBECTL) get deployments -n $(NAMESPACE)
	@echo ""
	@echo "=== PM4Py HPAs ==="
	$(KUBECTL) get hpa -n $(NAMESPACE) || echo "No HPAs found"

# Show logs
logs:
	$(KUBECTL) logs -n $(NAMESPACE) -l app=pm4py,component=api --tail=100 -f

# Port-forward services
port-forward:
	@echo "Port-forwarding services..."
	@echo "PM4Py API: http://localhost:8000"
	@echo "Grafana: http://localhost:3000"
	@echo "Jaeger: http://localhost:16686"
	@$(KUBECTL) port-forward -n $(NAMESPACE) svc/pm4py-api 8000:8000 &
	@$(KUBECTL) port-forward -n $(NAMESPACE) svc/grafana 3000:3000 &
	@$(KUBECTL) port-forward -n $(NAMESPACE) svc/jaeger 16686:16686 &
	@wait

# Restart API
restart:
	$(KUBECTL) rollout restart deployment/pm4py-api -n $(NAMESPACE)

# Scale API
scale:
	$(KUBECTL) scale deployment/pm4py-api -n $(NAMESPACE) --replicas=$(N)

# Clean everything including PVCs
clean:
	@echo "This will delete all PM4Py resources including persistent volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(MAKE) uninstall; \
		$(KUBECTL) delete pvc -n $(NAMESPACE) --all; \
		echo "Clean complete!"; \
	else \
		echo "Aborted."; \
	fi

# Quick health check
health:
	@echo "Checking PM4Py API health..."
	@$(KUBECTL) get pods -n $(NAMESPACE) -l app=pm4py,component=api -o jsonpath='{.items[0].status.phase}'
	@echo ""
