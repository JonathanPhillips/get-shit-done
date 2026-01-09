# Get Shit Done

**A Kubernetes-native Pomodoro timer and task management application**

Production-ready focus management web application deployed on k3s with comprehensive testing.

## Overview

Get Shit Done helps you stay focused and productive with:
- ✅ **Pomodoro Timer** - Work/break sessions with pause/resume/stop/skip
- ✅ **Task Manager** - Full CRUD operations with status management
- ✅ **Stats Dashboard** - Track sessions, work time, and productivity metrics
- ✅ **Persistent Storage** - SQLite database on Kubernetes PVC
- 🔄 **Future**: Claude AI integration for intelligent prompts
- 🔄 **Future**: GitHub activity tracking and project context
- 🔄 **Future**: Obsidian vault synchronization for note management

**Current Status**: Phase 1 Complete ✅ - MVP deployed and tested

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  k3s Cluster                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │   Frontend   │  │   Backend    │  │  Redis   │ │
│  │ React/TS     │──│  FastAPI     │──│  Cache   │ │
│  │ Tailwind     │  │  Python      │  │          │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
│         │                 │                         │
│         │                 ├─────> SQLite (PVC)      │
│         │                 ├─────> Obsidian (PVC)    │
│         │                 └─────> External APIs     │
│  ┌──────────────────────────────────────────────┐  │
│  │      Ingress: focus.localhost                 │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS
- Zustand (state management)
- React Query (API calls)
- Chart.js (analytics)

**Backend:**
- FastAPI (Python async framework)
- SQLAlchemy (ORM)
- Pydantic (validation)
- APScheduler (background tasks)
- aiofiles (file operations)

**Infrastructure:**
- K3s (Kubernetes)
- Docker (multi-stage builds)
- Redis (caching/sessions)
- SQLite (persistence)
- Traefik (ingress)

## Project Structure

```
focus_agent/
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration
│   │   ├── integrations/# External services (Claude, GitHub, Obsidian)
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # State management
│   │   ├── types/       # TypeScript types
│   │   └── utils/       # Utilities
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── k8s/                 # Kubernetes manifests
│   ├── base/            # Base configurations
│   └── overlays/        # Environment overlays
│       └── local/       # Local k3s config
├── docs/                # Documentation
├── scripts/             # Build/deploy scripts
└── README.md
```

## Quick Start

### Prerequisites

- k3s cluster running at 192.168.0.18:6443
- kubectl configured for cluster access
- Docker with insecure registry configured for 192.168.0.18:30500
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Build and Deploy to k3s

```bash
# Build images
./scripts/build.sh

# Deploy to k3s
kubectl apply -k k8s/overlays/local

# Check deployment
kubectl get pods -n focus-agent
kubectl get svc -n focus-agent
```

### Access Application

- **Web UI**: http://192.168.0.18:30100
- **API Health**: http://192.168.0.18:30100/api/health/detailed
- **API Docs**: http://192.168.0.18:30100/api/docs (if enabled)

## Features

### Phase 1: Foundation ✅ COMPLETE
- [x] Project structure and architecture
- [x] Docker multi-stage builds (backend & frontend)
- [x] FastAPI async backend with SQLAlchemy
- [x] React frontend with TypeScript & Tailwind
- [x] Pomodoro timer (work/break sessions with full controls)
- [x] Task manager (CRUD operations with status management)
- [x] K8s deployment to local cluster
- [x] Comprehensive testing (48 tests: 29 backend unit, 33 E2E)
- [x] Production deployment on k3s

### Phase 2: Integrations (Next)
- [ ] GitHub OAuth authentication
- [ ] GitHub activity tracking and metrics
- [ ] Obsidian file watcher and sync
- [ ] Markdown parser for notes
- [ ] Two-way note synchronization

### Phase 3: Claude AI Intelligence
- [ ] Claude API integration
- [ ] Session analyzer and insights
- [ ] AI-powered daily planning prompts
- [ ] Context-aware focus suggestions

### Phase 4: Analytics & Polish
- [ ] Advanced analytics dashboard
- [ ] Metrics visualization with charts
- [ ] WebSocket real-time updates
- [ ] Mobile app (React Native)

## Testing

**Backend Unit Tests (pytest)**:
- 29 tests covering Task and Pomodoro APIs
- ~95% API endpoint coverage
- Status: ✅ 29/29 passing (100%)

**E2E Tests (Playwright)**:
- 33 tests across 3 test suites
- Multi-browser support (Chrome, Firefox, Safari, Mobile)
- Pomodoro: ✅ 10/10 passing (100%)
- Tasks: 🔄 5/13 passing (38% - known selector issues)
- Integration: 📋 11 tests created

**Run Tests**:
```bash
# Backend unit tests
cd backend && pytest tests/ -v

# E2E tests
cd e2e-tests && npm test

# Specific suite
npx playwright test tests/pomodoro.spec.ts --project=chromium
```

See `docs/testing.md` for comprehensive testing documentation.

## Repository

**GitHub**: https://github.com/JonathanPhillips/get-shit-done

```bash
# Clone on new machine
git clone https://github.com/JonathanPhillips/get-shit-done.git
cd get-shit-done
```

## Documentation

- **CLAUDE.md** - Complete project documentation with deployment details
- **DEPLOYMENT_SUMMARY.md** - Quick setup guide for new environments
- **docs/testing.md** - Testing guide and troubleshooting
- **docs/quickstart.md** - Quick start for developers
- **docs/deployment.md** - Kubernetes deployment details

## Configuration

Current deployment uses:
- **k3s Cluster**: 192.168.0.18:6443
- **Container Registry**: 192.168.0.18:30500
- **Namespace**: focus-agent
- **Storage**: SQLite on PVC (local-path)
- **Cache**: Redis for sessions

See `CLAUDE.md` for complete configuration details.

## Contributing

This is a personal project, but suggestions and improvements are welcome! Please:
1. Review `CLAUDE.md` for architecture and design decisions
2. Ensure tests pass before submitting changes
3. Follow existing code style and patterns

## License

MIT

## Author

Jonathan Phillips - Home Lab K3s Project

**Built with**: FastAPI, React, TypeScript, Tailwind, Kubernetes, Docker
