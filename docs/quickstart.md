# Focus Agent - Quick Start

Get up and running with Focus Agent in 5 minutes.

## TL;DR - One Command Deployment

```bash
cd /Users/jon/Documents/code/focus_agent

# Create secrets (optional for Phase 1)
kubectl create namespace focus-agent
kubectl create secret generic focus-agent-secrets \
  --from-literal=secret-key="$(openssl rand -base64 32)" \
  --from-literal=claude-api-key="" \
  --from-literal=github-client-id="" \
  --from-literal=github-client-secret="" \
  -n focus-agent

# Build and deploy
make build deploy

# Wait for pods to be ready (2-3 minutes)
kubectl wait --for=condition=ready pod -l project=focus-agent -n focus-agent --timeout=300s

# Access the app
open http://192.168.0.18:30085
```

## Step-by-Step Quick Start

### 1. Prerequisites Check

```bash
# Verify k3s cluster
kubectl get nodes

# Verify Docker registry config
docker info | grep "192.168.0.18:30500"
```

If Docker registry not configured, add to Docker settings:
```json
{
  "insecure-registries": ["192.168.0.18:30500"]
}
```

### 2. Create Secrets

```bash
cd /Users/jon/Documents/code/focus_agent

# Create namespace
kubectl create namespace focus-agent

# Create minimal secrets
kubectl create secret generic focus-agent-secrets \
  --from-literal=secret-key="change-me-in-production" \
  -n focus-agent
```

### 3. Build & Deploy

```bash
# Build both images and push to registry
make build

# Deploy to k3s
make deploy

# Check status
make status
```

### 4. Verify Deployment

```bash
# Watch pods start
kubectl get pods -n focus-agent -w

# When all pods are Running, check health
curl http://192.168.0.18:30085/health
```

### 5. Access Application

**Web UI**: http://192.168.0.18:30085
**API Docs**: http://192.168.0.18:30085/docs
**Health Check**: http://192.168.0.18:30085/health/detailed

## What You Should See

### Home Page
- Welcome message
- 4 feature cards (Pomodoro, Tasks, GitHub, Obsidian)
- System status section showing:
  - Service info
  - Version
  - Environment
  - Component health (Database, Redis, Obsidian)

### Health Status
All components should show:
- Database: ✅ up
- Redis: ✅ up
- Obsidian: ⚠️ disabled (normal for Phase 1)

## Useful Commands

```bash
# View logs
make logs                 # All logs
make logs-backend        # Backend only
make logs-frontend       # Frontend only

# Shell access
make exec-backend        # Backend container
make exec-frontend       # Frontend container

# Restart
make clean-pods          # Restart all pods

# Rebuild & redeploy
make redeploy           # Build + deploy in one command

# Cleanup
make clean              # Remove everything
```

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl get events -n focus-agent --sort-by='.lastTimestamp'

# Check specific pod
kubectl describe pod -n focus-agent <pod-name>
```

### Can't Access Web UI

```bash
# Verify frontend service
kubectl get svc -n focus-agent focus-agent-frontend-service

# Should show NodePort 30085

# Test from command line
curl -I http://192.168.0.18:30085
```

### Image Pull Errors

```bash
# Verify images in registry
make registry-check

# Or manually
curl http://192.168.0.18:30500/v2/_catalog

# Rebuild if needed
make build
```

## Next Steps

1. ✅ Application deployed and running
2. Explore the API at http://192.168.0.18:30085/docs
3. Ready to implement features:
   - Pomodoro timer
   - Task manager
   - GitHub integration
   - Obsidian sync
   - Claude AI integration

## Getting Help

- Full deployment guide: `docs/deployment.md`
- Project overview: `README.md`
- Claude Code context: `CLAUDE.md`
- K8s cluster docs: `/Users/jon/Documents/code/kubernetes`

## Phase 1 Complete! 🎉

You now have:
- ✅ FastAPI backend with health checks
- ✅ React frontend with Tailwind CSS
- ✅ Redis for caching
- ✅ SQLite database
- ✅ Deployed to k3s cluster
- ✅ Accessible via NodePort and Ingress

Ready for Phase 2: Feature Implementation!
