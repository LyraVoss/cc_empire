#!/bin/bash
# Cloud Deployment Script
# Automates deployment to Azure Container Instance or App Service

set -e

echo "=========================================="
echo "🚀 CYBER CHEST DEPLOYMENT SCRIPT"
echo "=========================================="

# Configuration
IMAGE_NAME="cyber-chest"
IMAGE_TAG="latest"
REGISTRY="${REGISTRY_NAME}.azurecr.io"
RESOURCE_GROUP="${RESOURCE_GROUP_NAME}"
CONTAINER_NAME="cyber-chest-instance"
REGION="eastus"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed${NC}"
    exit 1
fi
if ! command -v az &> /dev/null; then
    echo -e "${RED}Azure CLI is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Prerequisites met${NC}"

# Build Docker image
echo -e "${YELLOW}[2/5] Building Docker image...${NC}"
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Start application
CMD ["python", "main.py"]
EOF

docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .
echo -e "${GREEN}✓ Docker image built${NC}"

# Push to Azure Container Registry
echo -e "${YELLOW}[3/5] Pushing to Azure Container Registry...${NC}"
az acr login --name ${REGISTRY_NAME}
docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
echo -e "${GREEN}✓ Image pushed to ACR${NC}"

# Deploy to Azure Container Instance
echo -e "${YELLOW}[4/5] Deploying to Azure Container Instance...${NC}"
az container create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${CONTAINER_NAME} \
    --image ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
    --cpu 2 \
    --memory 4 \
    --ports 8000 \
    --registry-username <admin-username> \
    --registry-password <admin-password> \
    --environment-variables \
        ENVIRONMENT=production \
        DEBUG=false \
        PORT=8000 \
    --query ipAddress.fqdn \
    --no-wait

echo -e "${GREEN}✓ Container deployment initiated${NC}"

# Show deployment status
echo -e "${YELLOW}[5/5] Deployment status...${NC}"
az container show --resource-group ${RESOURCE_GROUP} --name ${CONTAINER_NAME}

echo ""
echo -e "${GREEN}=========================================="
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================="${NC}
echo ""
echo "Next steps:"
echo "1. Wait for container to start (2-3 minutes)"
echo "2. Get the FQDN: az container show --resource-group ${RESOURCE_GROUP} --name ${CONTAINER_NAME} --query ipAddress.fqdn"
echo "3. Check health: curl http://<FQDN>:8000/health"
echo "4. Monitor logs: az container logs --resource-group ${RESOURCE_GROUP} --name ${CONTAINER_NAME} --follow"
