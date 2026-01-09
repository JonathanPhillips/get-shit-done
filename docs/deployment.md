# Focus Agent - Deployment Guide

Complete guide for deploying Focus Agent to your local k3s cluster.

## Prerequisites

### Required
- k3s cluster running at `192.168.0.18:6443`
- kubectl configured with cluster access
- Docker configured for insecure registry `192.168.0.18:30500`
- Make installed (for convenience commands)

### Verify Prerequisites

```bash
# Check k3s cluster access
kubectl get nodes

# Check Docker registry configuration
# Should have insecure registry configured in Docker daemon settings
docker info | grep "Insecure Registries"

# Verify Make is installed
make --version
```

### Configure Docker for Insecure Registry

**macOS:**
1. Docker Desktop → Settings → Docker Engine
2. Add to the JSON configuration:
```json
{
  "insecure-registries": ["192.168.0.18:30500"]
}
```
3. Click "Apply & Restart"

**Linux:**
Edit `/etc/docker/daemon.json`:
```json
{
  "insecure-registries": ["192.168.0.18:30500"]
}
```
Restart Docker: `sudo systemctl restart docker`

## Step 1: Create Secrets

Before deploying, create the secrets (optional for Phase 1, required for later phases):

```bash
# Generate a random secret key
SECRET_KEY=$(openssl rand -base64 32)

# Create the secret
kubectl create secret generic focus-agent-secrets \
  --from-literal=secret-key="$SECRET_KEY" \
  --from-literal=claude-api-key="" \
  --from-literal=github-client-id="" \
  --from-literal=github-client-secret="" \
  --namespace=focus-agent \
  --dry-run=client -o yaml | kubectl apply -f -
```

Note: Empty values are fine for Phase 1. You'll add actual API keys in later phases.

## Step 2: Build Docker Images

From the project root directory:

```bash
# Build and push both images to the registry
make build

# Or build individually
make build-backend
make build-frontend
```

This will:
1. Build backend Docker image
2. Build frontend Docker image
3. Push both to `192.168.0.18:30500`

### Verify Images in Registry

```bash
# Check backend image
curl http://192.168.0.18:30500/v2/focus-agent-backend/tags/list

# Check frontend image
curl http://192.168.0.18:30500/v2/focus-agent-frontend/tags/list

# Or use make command
make registry-check
```

## Step 3: Deploy to Kubernetes

```bash
# Deploy everything
make deploy

# Or manually with kubectl
kubectl apply -k k8s/overlays/local
```

This creates:
- `focus-agent` namespace
- ConfigMaps for environment variables
- PVCs for database and Obsidian vault
- Redis deployment and service
- Backend deployment and service
- Frontend deployment and service (NodePort on 30085)
- Ingress for `focus.localhost`

### Watch Deployment

```bash
# Watch pods starting up
kubectl get pods -n focus-agent -w

# Check all resources
make status

# Or manually
kubectl get all -n focus-agent
```

## Step 4: Verify Deployment

### Check Pod Status

```bash
# All pods should be Running
kubectl get pods -n focus-agent

# Expected output:
# NAME                                     READY   STATUS    RESTARTS   AGE
# focus-agent-backend-xxx                  1/1     Running   0          2m
# focus-agent-frontend-xxx                 1/1     Running   0          2m
# redis-xxx                                1/1     Running   0          2m
```

### Check Logs

```bash
# Backend logs
make logs-backend

# Frontend logs
make logs-frontend

# All logs
make logs
```

### Test Health Endpoints

```bash
# Test backend health check
curl http://192.168.0.18:30085/api/health

# Or via port-forward
kubectl port-forward -n focus-agent svc/focus-agent-backend-service 8000:8000
curl http://localhost:8000/health
```

## Step 5: Access the Application

### Option 1: NodePort (Easiest)

Access directly via NodePort:
- **URL**: http://192.168.0.18:30085
- **API Docs**: http://192.168.0.18:30085/docs

### Option 2: Ingress (focus.localhost)

Add to `/etc/hosts`:
```
192.168.0.18    focus.localhost
```

Access via:
- **URL**: http://focus.localhost

### Option 3: Port Forward (Development)

```bash
# Forward frontend
kubectl port-forward -n focus-agent svc/focus-agent-frontend-service 3000:80

# Forward backend
kubectl port-forward -n focus-agent svc/focus-agent-backend-service 8000:8000
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

## Common Operations

### Viewing Logs

```bash
# Tail backend logs
make logs-backend

# Tail frontend logs
make logs-frontend

# Describe resources for debugging
make describe
```

### Shell Access

```bash
# Exec into backend pod
make exec-backend

# Exec into frontend pod
make exec-frontend
```

### Update Deployment

After code changes:

```bash
# Rebuild and redeploy
make redeploy

# Or step by step
make build
make deploy
```

### Restart Pods

```bash
# Delete pods (they will auto-restart)
make clean-pods

# Or manually
kubectl delete pods -n focus-agent --all
```

## Troubleshooting

### Pods Not Starting

**Check Events:**
```bash
kubectl get events -n focus-agent --sort-by='.lastTimestamp'
```

**Describe Pod:**
```bash
POD_NAME=$(kubectl get pod -n focus-agent -l app=focus-agent-backend -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod -n focus-agent $POD_NAME
```

### Image Pull Errors

**Verify Registry Access:**
```bash
# From your machine
curl http://192.168.0.18:30500/v2/_catalog

# From within cluster
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
# Inside container:
apk add curl
curl http://192.168.0.18:30500/v2/_catalog
```

**Rebuild and Push:**
```bash
make build
```

### Database Issues

**Check PVC:**
```bash
kubectl get pvc -n focus-agent
kubectl describe pvc focus-agent-db-pvc -n focus-agent
```

**Check Database File:**
```bash
make exec-backend
# Inside container:
ls -la /app/data/
```

### Redis Connection Issues

**Check Redis Pod:**
```bash
kubectl logs -n focus-agent -l app=redis --tail=50
```

**Test Redis Connection:**
```bash
# Port forward Redis
kubectl port-forward -n focus-agent svc/redis-service 6379:6379

# Test with redis-cli
redis-cli -h localhost ping
```

### Frontend Can't Reach Backend

**Check Service Endpoints:**
```bash
kubectl get endpoints -n focus-agent
```

**Check Network Policy:**
```bash
kubectl get networkpolicies -n focus-agent
```

**Test from Frontend Pod:**
```bash
kubectl exec -it -n focus-agent $(kubectl get pod -n focus-agent -l app=focus-agent-frontend -o jsonpath='{.items[0].metadata.name}') -- sh

# Inside container:
wget -O- http://focus-agent-backend-service:8000/health
```

## Cleanup

### Remove Deployment

```bash
# Remove all resources
make clean

# Or manually
kubectl delete namespace focus-agent
```

### Remove Images from Registry

Images will remain in the registry. To clean up:

```bash
# SSH to k3s node
ssh user@192.168.0.18

# Remove images (adjust path based on your registry setup)
# This depends on how your registry is configured
```

## Next Steps

After successful deployment:

1. **Verify Health**: Check `/health/detailed` endpoint shows all systems up
2. **Test API**: Explore API documentation at `/docs`
3. **Phase 2**: Implement Pomodoro timer and task manager
4. **Phase 3**: Add GitHub and Obsidian integrations
5. **Phase 4**: Implement Claude AI integration

## Monitoring

### Prometheus Metrics

Backend exposes Prometheus metrics at `/metrics`:
```bash
curl http://192.168.0.18:30085/metrics
```

### Grafana Dashboard

If you have Grafana running in your cluster:
- URL: http://192.168.0.18:30030
- Add Focus Agent metrics to a dashboard

## Security Considerations

**Current Setup (Phase 1):**
- Running in homelab environment
- No authentication required
- Insecure registry (HTTP)
- Secrets optional

**Future Enhancements:**
- Add authentication/authorization
- Use HTTPS with cert-manager
- Secure registry with TLS
- Network policies for pod-to-pod communication
- Resource quotas and limits

## Support

For issues:
1. Check logs: `make logs`
2. Check pod status: `make status`
3. Review CLAUDE.md for project context
4. Consult k8s documentation in `/Users/jon/Documents/code/kubernetes`

Last updated: 2026-01-08
