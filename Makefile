.PHONY: help build deploy clean dev-backend dev-frontend test

# Variables
REGISTRY := 192.168.0.18:30500
PROJECT := focus-agent
NAMESPACE := focus-agent
BACKEND_IMAGE := $(REGISTRY)/$(PROJECT)-backend
FRONTEND_IMAGE := $(REGISTRY)/$(PROJECT)-frontend
VERSION := latest

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
dev-backend: ## Run backend in development mode
	cd backend && python -m venv venv && \
	. venv/bin/activate && \
	pip install -r requirements.txt && \
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in development mode
	cd frontend && npm install && npm run dev

dev: ## Run both frontend and backend in development mode
	@echo "Starting backend and frontend..."
	@make -j2 dev-backend dev-frontend

# Build
build-backend: ## Build backend Docker image
	docker build -t $(BACKEND_IMAGE):$(VERSION) ./backend
	docker push $(BACKEND_IMAGE):$(VERSION)

build-frontend: ## Build frontend Docker image
	docker build -t $(FRONTEND_IMAGE):$(VERSION) ./frontend
	docker push $(FRONTEND_IMAGE):$(VERSION)

build: build-backend build-frontend ## Build all Docker images

# Deploy
create-namespace: ## Create k8s namespace
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -

deploy: create-namespace ## Deploy to k8s cluster
	kubectl apply -k k8s/overlays/local

redeploy: build deploy ## Rebuild and redeploy

# Operations
logs-backend: ## Tail backend logs
	kubectl logs -n $(NAMESPACE) -l app=$(PROJECT)-backend --tail=100 -f

logs-frontend: ## Tail frontend logs
	kubectl logs -n $(NAMESPACE) -l app=$(PROJECT)-frontend --tail=100 -f

logs: ## Tail all logs
	kubectl logs -n $(NAMESPACE) -l project=$(PROJECT) --tail=100 -f

status: ## Show deployment status
	kubectl get all -n $(NAMESPACE)

describe: ## Describe all resources
	kubectl describe all -n $(NAMESPACE)

exec-backend: ## Exec into backend pod
	kubectl exec -it -n $(NAMESPACE) $$(kubectl get pod -n $(NAMESPACE) -l app=$(PROJECT)-backend -o jsonpath='{.items[0].metadata.name}') -- /bin/bash

exec-frontend: ## Exec into frontend pod
	kubectl exec -it -n $(NAMESPACE) $$(kubectl get pod -n $(NAMESPACE) -l app=$(PROJECT)-frontend -o jsonpath='{.items[0].metadata.name}') -- /bin/sh

# Testing
test-backend: ## Run backend tests
	cd backend && pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

test: test-backend test-frontend ## Run all tests

# Cleanup
clean-pods: ## Delete all pods (will restart)
	kubectl delete pods -n $(NAMESPACE) --all

clean-deploy: ## Delete deployment
	kubectl delete -k k8s/overlays/local

clean: clean-deploy ## Full cleanup
	kubectl delete namespace $(NAMESPACE)

# Registry
registry-check: ## Check images in registry
	@echo "Backend images:"
	@curl -s http://$(REGISTRY)/v2/$(PROJECT)-backend/tags/list | jq .
	@echo "\nFrontend images:"
	@curl -s http://$(REGISTRY)/v2/$(PROJECT)-frontend/tags/list | jq .

# Port forwarding
port-forward-backend: ## Port forward backend to localhost:8000
	kubectl port-forward -n $(NAMESPACE) svc/$(PROJECT)-backend-service 8000:8000

port-forward-frontend: ## Port forward frontend to localhost:3000
	kubectl port-forward -n $(NAMESPACE) svc/$(PROJECT)-frontend-service 3000:80

port-forward-redis: ## Port forward Redis to localhost:6379
	kubectl port-forward -n $(NAMESPACE) svc/redis-service 6379:6379
