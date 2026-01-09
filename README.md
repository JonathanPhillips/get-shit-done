# Focus Agent

Kubernetes-based focus management web application with Claude AI, GitHub, Obsidian, and productivity integrations.

## Overview

Focus Agent is an intelligent work focus assistant that runs in your local k3s cluster, helping you:
- Plan and track your daily tasks
- Integrate with Claude for AI-powered insights
- Connect GitHub activity and project context
- Sync with your Obsidian vault for note management
- Use Pomodoro timer for structured work sessions
- Monitor focus metrics and productivity analytics

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

- **Web UI**: http://focus.localhost (or http://192.168.0.18:30085)
- **API Docs**: http://192.168.0.18:30085/docs
- **Health Check**: http://192.168.0.18:30085/health

## Features (Planned)

### Phase 1: Foundation
- [x] Project structure
- [ ] Docker multi-stage builds
- [ ] Basic FastAPI backend
- [ ] React frontend with Tailwind
- [ ] Pomodoro timer
- [ ] Task manager (CRUD)
- [ ] K8s deployment

### Phase 2: Integrations
- [ ] GitHub OAuth
- [ ] GitHub activity tracking
- [ ] Obsidian file watcher
- [ ] Markdown parser
- [ ] Note sync

### Phase 3: Claude AI
- [ ] Claude API integration
- [ ] Session analyzer
- [ ] Daily planning prompts
- [ ] Focus suggestions

### Phase 4: Analytics
- [ ] Dashboard
- [ ] Metrics visualization
- [ ] WebSocket updates
- [ ] Advanced features

## Configuration

See `docs/configuration.md` for detailed configuration options.

## Development

See `docs/development.md` for development guidelines and contribution workflow.

## Deployment

See `docs/deployment.md` for deployment instructions and k8s configuration.

## License

MIT

## Author

Jon - Home Lab Project
