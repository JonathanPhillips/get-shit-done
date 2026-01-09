#!/bin/bash
set -e

# Configuration
REGISTRY="192.168.0.18:30500"
PROJECT="focus-agent"
VERSION="${1:-latest}"

echo "========================================"
echo "Building Focus Agent v${VERSION}"
echo "========================================"

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo -e "${BLUE}Building backend image...${NC}"
cd "$PROJECT_ROOT/backend"
docker build -t ${REGISTRY}/${PROJECT}-backend:${VERSION} .

echo ""
echo -e "${BLUE}Building frontend image...${NC}"
cd "$PROJECT_ROOT/frontend"
docker build -t ${REGISTRY}/${PROJECT}-frontend:${VERSION} .

echo ""
echo -e "${BLUE}Pushing images to registry...${NC}"
docker push ${REGISTRY}/${PROJECT}-backend:${VERSION}
docker push ${REGISTRY}/${PROJECT}-frontend:${VERSION}

echo ""
echo -e "${GREEN}✓ Build complete!${NC}"
echo ""
echo "Images pushed:"
echo "  - ${REGISTRY}/${PROJECT}-backend:${VERSION}"
echo "  - ${REGISTRY}/${PROJECT}-frontend:${VERSION}"
echo ""
echo "Verify with:"
echo "  curl http://${REGISTRY}/v2/${PROJECT}-backend/tags/list"
echo "  curl http://${REGISTRY}/v2/${PROJECT}-frontend/tags/list"
echo ""
echo "Deploy with:"
echo "  kubectl apply -k k8s/overlays/local"
echo ""
