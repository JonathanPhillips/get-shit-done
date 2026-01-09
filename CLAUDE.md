# CLAUDE.md - Focus Agent Project

## Project Overview

**Focus Agent** is a Kubernetes-native web application designed to enhance work focus and productivity through intelligent integrations with Claude AI, GitHub, Obsidian, and productivity tools.

## Purpose

This application runs in a local k3s cluster to provide:
- AI-powered daily planning and focus prompts (Claude integration)
- GitHub activity tracking and project context
- Obsidian vault synchronization and note management
- Pomodoro timer with distraction blocking
- Analytics dashboard for productivity metrics

## Quick Reference

**Access Points**:
- **Web UI**: http://192.168.0.18:30100
- **API Health**: http://192.168.0.18:30100/api/health/detailed
- **Registry**: http://192.168.0.18:30500/v2/_catalog
- **Namespace**: `focus-agent`

**Common Commands**:
```bash
# Check deployment status
kubectl get pods -n focus-agent

# View logs
kubectl logs -n focus-agent deployment/focus-agent-backend --tail=50 -f
kubectl logs -n focus-agent deployment/focus-agent-frontend --tail=50

# Rebuild and redeploy backend
cd backend && docker build -t 192.168.0.18:30500/focus-agent-backend:latest . && \
docker push 192.168.0.18:30500/focus-agent-backend:latest && \
kubectl rollout restart deployment focus-agent-backend -n focus-agent

# Run tests
cd e2e-tests && npm test  # E2E tests
cd backend && pytest tests/ -v  # Backend unit tests

# Check active sessions (for debugging)
curl http://192.168.0.18:30100/api/pomodoro/sessions?status=active
```

**Git Repository**:
- **GitHub Repo**: https://github.com/JonathanPhillips/get-shit-done
- **Clone URL**: `git clone https://github.com/JonathanPhillips/get-shit-done.git`
- **Main Branch**: `main`
- **Current Status**: Phase 1 complete with testing infrastructure

## Architecture

### Components

**Frontend (React/TypeScript/Tailwind)**
- **Location**: `/frontend`
- **Dev Port**: 3000 (Vite dev server)
- **Prod Port**: 80 (Nginx)
- **Build**: Multi-stage Docker (node:20 build → nginx:alpine production)
- **Key Files**:
  - `src/components/PomodoroTimer.tsx` - Main timer component
  - `src/components/TaskManager.tsx` - Task management UI
  - `src/api/pomodoro.ts` - Pomodoro API client
  - `src/api/tasks.ts` - Task API client
- **Nginx Config**: `/frontend/nginx.conf` - API proxy and SPA routing

**Backend (FastAPI/Python 3.11)**
- **Location**: `/backend`
- **Port**: 8000
- **Features**: Async API with SQLAlchemy, WebSocket support (future), background tasks
- **Key Files**:
  - `src/main.py` - FastAPI application entry point
  - `src/api/pomodoro.py` - Pomodoro session endpoints
  - `src/api/tasks.py` - Task CRUD endpoints
  - `src/models/pomodoro.py` - PomodoroSession SQLAlchemy model
  - `src/models/task.py` - Task SQLAlchemy model
  - `src/core/database.py` - Async database configuration
- **Build**: Multi-stage Docker (dependencies → production with non-root user)
- **Workers**: Single worker only (SQLite limitation)

**Database**
- **SQLite**: Primary data storage (`/app/data/focus_agent.db` in pod)
- **Redis**: Session management and caching
- **Schema**: Auto-created on startup via SQLAlchemy metadata

**Storage**
- **Database PVC**: `focus-agent-database-pvc` (1Gi, local-path)
- **Future**: Obsidian vault PVC (read-only by default)

### Deployment

**K3s Cluster Environment**:
- **Cluster API**: `192.168.0.18:6443`
- **Container Registry**: `192.168.0.18:30500` (insecure registry)
- **Namespace**: `focus-agent`
- **Web Access**: `http://192.168.0.18:30100` (NodePort)

**Registry Access**:
```bash
# Verify registry connectivity
curl http://192.168.0.18:30500/v2/_catalog

# List image tags
curl http://192.168.0.18:30500/v2/focus-agent-backend/tags/list
curl http://192.168.0.18:30500/v2/focus-agent-frontend/tags/list
```

**Kubernetes Manifests** (`/k8s`):
- **Base**: `/k8s/base/` - Environment-agnostic resources
  - `backend-deployment.yaml` - Backend deployment (1 replica)
  - `frontend-deployment.yaml` - Frontend deployment (1 replica)
  - `redis-deployment.yaml` - Redis deployment (1 replica)
  - `database-pvc.yaml` - SQLite database persistent volume claim
  - `kustomization.yaml` - Base kustomization
- **Overlay**: `/k8s/overlays/local/` - Local k3s environment
  - `kustomization.yaml` - Environment-specific patches
  - `configmap.yaml` - Backend environment variables

**Access URLs**:
- **Web UI**: http://192.168.0.18:30100
- **API Health**: http://192.168.0.18:30100/api/health/detailed
- **API Docs**: http://192.168.0.18:30100/api/docs (future - if enabled)

## Development Workflow

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Build and Deploy

**Complete Deployment Workflow**:

```bash
# 1. Build Backend Docker Image
cd /path/to/focus_agent/backend
docker build -t 192.168.0.18:30500/focus-agent-backend:latest .
docker push 192.168.0.18:30500/focus-agent-backend:latest

# 2. Build Frontend Docker Image
cd /path/to/focus_agent/frontend
docker build -t 192.168.0.18:30500/focus-agent-frontend:latest .
docker push 192.168.0.18:30500/focus-agent-frontend:latest

# 3. Deploy to k3s (first time)
kubectl apply -k k8s/overlays/local

# 3. OR Update existing deployment (after code changes)
kubectl rollout restart deployment focus-agent-backend -n focus-agent
kubectl rollout restart deployment focus-agent-frontend -n focus-agent

# 4. Wait for rollout to complete
kubectl rollout status deployment focus-agent-backend -n focus-agent --timeout=60s
kubectl rollout status deployment focus-agent-frontend -n focus-agent --timeout=60s

# 5. Check status
kubectl get pods -n focus-agent
kubectl get svc -n focus-agent
kubectl logs -n focus-agent -l app=focus-agent-backend --tail=50 -f

# 6. Verify deployment
curl http://192.168.0.18:30100
curl http://192.168.0.18:30100/api/health/detailed
```

**Quick Redeploy After Code Changes**:
```bash
# Backend changes
cd backend && docker build -t 192.168.0.18:30500/focus-agent-backend:latest . && docker push 192.168.0.18:30500/focus-agent-backend:latest && kubectl rollout restart deployment focus-agent-backend -n focus-agent

# Frontend changes
cd frontend && docker build -t 192.168.0.18:30500/focus-agent-frontend:latest . && docker push 192.168.0.18:30500/focus-agent-frontend:latest && kubectl rollout restart deployment focus-agent-frontend -n focus-agent
```

### Testing

**Backend Unit Tests (pytest)**:
```bash
cd backend
pip install -r requirements.txt  # if not already installed
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_tasks_api.py -v
pytest tests/test_pomodoro_api.py -v

# Run in Docker (matches production environment)
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  192.168.0.18:30500/focus-agent-backend:latest \
  pytest tests/ -v
```

**E2E Tests (Playwright)**:
```bash
cd e2e-tests
npm install  # first time only
npx playwright install  # install browsers (first time only)

# Run all E2E tests
npm test

# Run specific test suite
npx playwright test tests/pomodoro.spec.ts --project=chromium
npx playwright test tests/tasks.spec.ts --project=chromium
npx playwright test tests/integration.spec.ts --project=chromium

# Run in headed mode (see browser)
npm run test:headed

# Run in debug mode
npm run test:debug

# Run in UI mode (interactive)
npm run test:ui

# Test against different environment
BASE_URL=http://192.168.0.18:30100 npm test
```

**Test Coverage**:
- Backend: 29 unit tests (~95% API coverage)
- E2E: 33 Playwright tests (Pomodoro: 10/10 ✅, Tasks: 5/13 🔄, Integration: 11)
- Total: 48 automated tests

## Configuration

### Environment Variables

**Backend (via ConfigMap)**
- `DATABASE_URL`: `sqlite+aiosqlite:////app/data/focus_agent.db` (note: 4 slashes for absolute path)
- `REDIS_URL`: `redis://redis:6379/0`
- `OBSIDIAN_VAULT_PATH`: `/app/obsidian` (future use)
- `CLAUDE_API_KEY`: Claude API key (from Secret - future use)
- `GITHUB_CLIENT_ID`: GitHub OAuth client ID (future use)
- `GITHUB_CLIENT_SECRET`: GitHub OAuth secret (from Secret - future use)

**Frontend (via build-time env)**
- `VITE_API_URL`: `/api` (proxied through Nginx in production)

### Current Kubernetes Resources

**Deployed Resources** (namespace: `focus-agent`):
```bash
# Check all resources
kubectl get all -n focus-agent

# Should show:
# - deployment.apps/focus-agent-backend (1/1 ready)
# - deployment.apps/focus-agent-frontend (1/1 ready)
# - deployment.apps/redis (1/1 ready)
# - service/focus-agent-backend-service (ClusterIP)
# - service/focus-agent-frontend-service (NodePort 30100)
# - service/redis (ClusterIP)
# - persistentvolumeclaim/focus-agent-database-pvc (Bound)
```

### Secrets Management

**Current Setup** (Phase 1 - No secrets required yet):
```bash
# Create namespace (if doesn't exist)
kubectl create namespace focus-agent

# Future: Create secrets for Phase 2+
kubectl create secret generic focus-agent-secrets \
  --from-literal=claude-api-key=YOUR_KEY \
  --from-literal=github-client-secret=YOUR_SECRET \
  -n focus-agent
```

### Storage Setup

**Database PVC**:
- **PVC Name**: `focus-agent-database-pvc`
- **Storage Class**: `local-path` (k3s default)
- **Size**: 1Gi
- **Access Mode**: ReadWriteOnce
- **Host Path**: `/mnt/kubernetes-storage/focus-agent/database/` (on k3s node)

**Verify Storage**:
```bash
# Check PVC status
kubectl get pvc -n focus-agent

# Check actual files on k3s node
ssh user@192.168.0.18
ls -la /mnt/kubernetes-storage/focus-agent/database/
# Should show: focus_agent.db

# Access from pod
kubectl exec -it -n focus-agent deployment/focus-agent-backend -- ls -la /app/data
```

## Integrations

### Claude AI
- API integration for intelligent prompts
- Session context analysis
- Daily planning suggestions
- Real-time focus recommendations

### GitHub
- OAuth authentication
- Activity tracking (commits, PRs, issues)
- Project context extraction
- Webhook support (optional)

### Obsidian
- File watcher for vault changes
- Markdown parsing for TODOs
- Daily note creation
- Two-way sync (configurable)

## Recent Accomplishments

- 2026-01-08: Initial project structure created
- 2026-01-08: K8s infrastructure reviewed and documented
- 2026-01-09: Phase 1 MVP successfully deployed to k3s cluster
  - Created multi-stage Docker builds for backend and frontend
  - Implemented FastAPI backend with health checks and async database
  - Set up React frontend with Tailwind CSS and Vite
  - Configured Kubernetes manifests with Kustomize overlays
  - Fixed SQLite aiosqlite path format (required 4 slashes for absolute paths)
  - Added fsGroup security context for proper volume permissions
  - Changed to single-worker Uvicorn for SQLite compatibility
  - All services deployed and healthy (backend, frontend, redis)
  - Web UI accessible at http://192.168.0.18:30100
- 2026-01-09: Phase 1 Complete - Core Features Implemented
  - **Backend API**: Full task and Pomodoro session management
    - Created SQLAlchemy models for Task and PomodoroSession
    - Implemented complete REST API with CRUD operations
    - Added Pomodoro stats endpoint with session tracking
    - Task status management (todo, in_progress, completed, archived)
    - Pomodoro session lifecycle (active, completed, interrupted)
  - **Frontend UI**: Fully functional Pomodoro timer and task manager
    - Interactive Pomodoro timer with work/break sessions
    - Auto-advancing sessions with configurable durations
    - Real-time countdown display with progress bar
    - Task manager with create, update, delete, complete operations
    - Task filtering by status
    - Stats dashboard showing today's sessions and work time
  - **Testing**: All APIs tested and operational
  - **Deployment**: Both frontend and backend deployed to k3s cluster
- 2026-01-09: Comprehensive Test Suite Implemented
  - **Backend Unit Tests**: 29 pytest tests covering Task and Pomodoro APIs
    - In-memory SQLite for isolated test execution
    - Full CRUD operation coverage
    - Edge case and error handling tests
    - ~95% API endpoint coverage
  - **E2E Tests**: 33 Playwright tests for web UI
    - Pomodoro timer functionality (start/pause/stop/skip)
    - Task manager operations (create/update/delete/filter)
    - Integration tests (cross-feature interactions)
    - Multi-browser support (Chrome, Firefox, Safari, Mobile)
    - Responsive design validation
  - **Total**: 48 automated tests ensuring code quality
  - **Documentation**: Complete testing guide in `/docs/testing.md`
- 2026-01-09: Critical Bug Fixes & Test Infrastructure Hardening
  - **CRITICAL FIX**: Multiple active Pomodoro sessions causing database errors
    - **Root Cause**: `scalar_one_or_none()` failing when multiple active sessions existed in database
    - **Solution**: Changed to `.scalars().all()` and loop through all active sessions to interrupt them
    - **Endpoints Fixed**: `start_session()` and `get_active_session()` in `/backend/src/api/pomodoro.py`
    - **Impact**: Session creation now works reliably, auto-interrupts all previous active sessions
  - **E2E Test Results After Fixes**:
    - ✅ Pomodoro Timer: 10/10 tests passing (100%) - all session lifecycle tests working
    - 🔄 Task Manager: 5/13 tests passing (38%) - component selector mismatches identified for future fixes
    - 📋 Integration: 11 tests created (ready for validation)
  - **Test Infrastructure Improvements**:
    - Added `beforeEach` cleanup hooks to interrupt active sessions before each test
    - Fixed strict mode violations with `exact: true` selectors
    - Added `waitForLoadState('networkidle')` for proper page loading
    - Resolved test interference issues from parallel execution
  - **Docker Image Updates**: Backend redeployed to k3s with bug fixes

## Next Steps

### Phase 1: Foundation (COMPLETE ✅)
- [x] Create Docker multi-stage builds
- [x] Implement basic FastAPI backend with health checks
- [x] Set up React frontend with Tailwind CSS
- [x] Deploy to k3s cluster
- [x] Implement Pomodoro timer engine
- [x] Create task manager with CRUD API

### Phase 2: Integrations
- [ ] GitHub OAuth and activity tracking
- [ ] Obsidian file watcher and sync
- [ ] Markdown parser for notes

### Phase 3: Claude Intelligence
- [ ] Claude API integration
- [ ] Session analyzer
- [ ] Daily planning prompts

### Phase 4: Analytics & Polish
- [ ] Metrics dashboard
- [ ] WebSocket real-time updates
- [ ] Advanced features

## Port Allocations

Following the k3s cluster port allocation scheme:
- **30100**: Focus Agent web UI (NodePort) - ACTIVE
- **30085**: outfit-visualizer (allocated)
- **30086**: nfl-rag-chat (allocated)
- **30087**: argocd-server (allocated)

## Storage Locations

On k3s cluster node (`/mnt/kubernetes-storage/`):
- `focus-agent/database/`: SQLite database files
- `focus-agent/obsidian/`: Obsidian vault mount point (symlink to actual vault)

## Monitoring

### Health Checks
- Backend: `http://focus-agent-backend-service:8000/health/detailed` (internal)
- Frontend: `http://192.168.0.18:30100` (external)
- Full system: All pods should show 1/1 Ready in `kubectl get pods -n focus-agent`

### Metrics
- Prometheus metrics endpoint: `/metrics`
- Grafana dashboard: http://192.168.0.18:30030

## Troubleshooting

### Common Issues

**Pod won't start**
```bash
# Describe pod to see events
kubectl describe pod -n focus-agent <pod-name>

# Check logs
kubectl logs -n focus-agent <pod-name>
kubectl logs -n focus-agent <pod-name> --previous  # if pod crashed

# Get all pods status
kubectl get pods -n focus-agent -o wide
```

**Database connection issues**
```bash
# Check if database file exists
kubectl exec -it -n focus-agent deployment/focus-agent-backend -- ls -la /app/data

# Check database permissions
kubectl exec -it -n focus-agent deployment/focus-agent-backend -- stat /app/data/focus_agent.db

# Check PVC binding
kubectl get pvc -n focus-agent
kubectl describe pvc focus-agent-database-pvc -n focus-agent

# Manual database access (if needed)
kubectl exec -it -n focus-agent deployment/focus-agent-backend -- python3
>>> from src.core.database import engine, Base
>>> # Database operations here
```

**Image pull errors**
```bash
# Verify registry connectivity
curl http://192.168.0.18:30500/v2/_catalog

# Check specific image tags
curl http://192.168.0.18:30500/v2/focus-agent-backend/tags/list
curl http://192.168.0.18:30500/v2/focus-agent-frontend/tags/list

# Verify pod image pull status
kubectl describe pod -n focus-agent <pod-name> | grep -A 5 "Events:"
```

**API not responding**
```bash
# Check backend service
kubectl get svc -n focus-agent

# Test backend directly (from another pod)
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://focus-agent-backend-service:8000/health/detailed

# Check backend logs for errors
kubectl logs -n focus-agent deployment/focus-agent-backend --tail=100 -f

# Test API through NodePort
curl http://192.168.0.18:30100/api/health/detailed
```

**Frontend not loading**
```bash
# Check frontend service
kubectl get svc -n focus-agent focus-agent-frontend-service

# Check frontend logs
kubectl logs -n focus-agent deployment/focus-agent-frontend --tail=50

# Verify Nginx is serving files
kubectl exec -it -n focus-agent deployment/focus-agent-frontend -- ls -la /usr/share/nginx/html

# Test frontend directly
curl http://192.168.0.18:30100
```

**E2E Tests failing**
```bash
# Ensure no active sessions interfering with tests
curl -X POST http://192.168.0.18:30100/api/pomodoro/sessions/{id}/interrupt

# Check all active sessions
curl http://192.168.0.18:30100/api/pomodoro/sessions?status=active

# Clear test data (if needed)
kubectl exec -it -n focus-agent deployment/focus-agent-backend -- rm /app/data/focus_agent.db
kubectl rollout restart deployment focus-agent-backend -n focus-agent
```

### Known Issues & Solutions

**SQLite "unable to open database file" error**
- **Solution**: Use 4 slashes in DATABASE_URL for absolute paths: `sqlite+aiosqlite:////app/data/focus_agent.db`
- **Reason**: aiosqlite requires explicit absolute path notation

**Volume permission errors**
- **Solution**: Add `securityContext.fsGroup: 1000` to pod spec
- **Reason**: Mounted volumes need group ownership matching the non-root user

**Multi-worker issues with SQLite**
- **Solution**: Use single Uvicorn worker (`uvicorn src.main:app` without `--workers`)
- **Reason**: SQLite doesn't support concurrent writes from multiple processes

**NodePort conflicts**
- **Solution**: Check existing allocations with `kubectl get svc --all-namespaces | grep NodePort`
- **Used ports**: 30085 (outfit-visualizer), 30086 (nfl-rag-chat), 30087 (argocd)

## Setting Up on New Machine

### Prerequisites

**Required**:
- Docker installed and running
- kubectl configured for k3s cluster at 192.168.0.18:6443
- Network access to k3s cluster and registry (192.168.0.18:30500)
- Git for cloning repository

**Verify Cluster Access**:
```bash
# Test kubectl connectivity
kubectl get nodes
kubectl get namespaces

# Test registry access
curl http://192.168.0.18:30500/v2/_catalog

# Test web access
curl http://192.168.0.18:30100
```

### First-Time Setup (if cluster is down)

```bash
# 1. Clone repository
git clone https://github.com/JonathanPhillips/get-shit-done.git focus_agent
cd focus_agent

# 2. Create namespace
kubectl create namespace focus-agent

# 3. Create storage directory on k3s node (if doesn't exist)
ssh user@192.168.0.18
sudo mkdir -p /mnt/kubernetes-storage/focus-agent/database
sudo chown -R 1000:1000 /mnt/kubernetes-storage/focus-agent
exit

# 4. Build and push images
cd backend
docker build -t 192.168.0.18:30500/focus-agent-backend:latest .
docker push 192.168.0.18:30500/focus-agent-backend:latest

cd ../frontend
docker build -t 192.168.0.18:30500/focus-agent-frontend:latest .
docker push 192.168.0.18:30500/focus-agent-frontend:latest

# 5. Deploy to k3s
cd ..
kubectl apply -k k8s/overlays/local

# 6. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=focus-agent-backend -n focus-agent --timeout=120s
kubectl wait --for=condition=ready pod -l app=focus-agent-frontend -n focus-agent --timeout=120s

# 7. Verify deployment
kubectl get all -n focus-agent
curl http://192.168.0.18:30100/api/health/detailed
```

### Continuing Development (if cluster is already running)

```bash
# 1. Clone repository
git clone https://github.com/JonathanPhillips/get-shit-done.git focus_agent
cd focus_agent

# 2. Verify cluster is running
kubectl get pods -n focus-agent

# 3. Make code changes
# ... edit files ...

# 4. Rebuild and redeploy (backend example)
cd backend
docker build -t 192.168.0.18:30500/focus-agent-backend:latest .
docker push 192.168.0.18:30500/focus-agent-backend:latest
kubectl rollout restart deployment focus-agent-backend -n focus-agent
kubectl rollout status deployment focus-agent-backend -n focus-agent --timeout=60s

# 5. Test changes
curl http://192.168.0.18:30100/api/health/detailed
cd ../e2e-tests
npm test
```

### Development Environment Setup

**For Backend Development**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pytest tests/ -v  # Run tests locally
```

**For Frontend Development**:
```bash
cd frontend
npm install
npm run dev  # Start dev server on http://localhost:3000
```

**For E2E Testing**:
```bash
cd e2e-tests
npm install
npx playwright install chromium  # Only chromium needed for basic testing
npm test
```

## Current Deployment Status

**Last Deployed**: 2026-01-09
**Deployment Location**: k3s cluster at 192.168.0.18
**Status**: ✅ Fully operational

**Current Images in Registry**:
- `192.168.0.18:30500/focus-agent-backend:latest` - Backend with bug fixes (2026-01-09)
- `192.168.0.18:30500/focus-agent-frontend:latest` - Frontend (2026-01-09)

**Active Features**:
- ✅ Pomodoro Timer (work/break sessions, pause/resume/stop/skip)
- ✅ Task Manager (create/update/delete/complete/filter)
- ✅ Stats Dashboard (today's sessions, work time, total sessions, streak)
- ✅ Persistent Storage (SQLite database on PVC)
- ✅ Redis caching
- ✅ Health monitoring endpoints

**Test Coverage**:
- Backend Unit Tests: 29/29 passing (100%)
- E2E Pomodoro Tests: 10/10 passing (100%)
- E2E Task Tests: 5/13 passing (38% - known selector issues)
- E2E Integration Tests: Not yet run

**Known Issues**:
- Task Manager E2E tests have selector mismatches (8/13 failing) - component UI vs test expectations
- Integration tests not yet validated

## Contact

**Author**: Jon
**Environment**: macOS development, k3s homelab deployment (192.168.0.18)
**Documentation**: This file, `/docs` directory, main `README.md`

Last updated: 2026-01-09
