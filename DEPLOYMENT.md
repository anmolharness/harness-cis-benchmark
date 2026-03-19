# Harness CIS Benchmark Agent - Deployment Guide

A production-ready security compliance dashboard for Harness customers.

## Overview

This agent provides:
- ✅ 41 comprehensive security and operational checks
- 📊 Interactive web dashboard with drill-down analytics
- 🔄 One-click compliance scanning
- 🚀 Production-ready with Docker deployment
- 🔒 Secure, isolated execution

## Quick Start for Customers

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed
- Harness API key with read access
- Harness Account ID

**Steps:**

1. **Download the agent:**
```bash
# Clone or download the repository
git clone <repository-url>
cd harness-cis-benchmark
```

2. **Configure credentials:**
Create `.env` file:
```bash
HARNESS_API_KEY=your_api_key_here
HARNESS_ACCOUNT_ID=your_account_id_here
```

3. **Launch the dashboard:**
```bash
docker-compose up -d
```

4. **Access the dashboard:**
Open http://localhost:5000 in your browser

5. **Run your first scan:**
Click the "🔄 Run New Scan" button

### Option 2: Python (Development)

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export HARNESS_API_KEY=your_api_key_here
export HARNESS_ACCOUNT_ID=your_account_id_here

# Run dashboard
python3 dashboard.py
```

## Production Deployment

### Docker with Custom Port

```bash
# Run on custom port (e.g., 8080)
docker run -d \
  -p 8080:5000 \
  -e HARNESS_API_KEY=your_key \
  -e HARNESS_ACCOUNT_ID=your_account \
  --name harness-cis-agent \
  harness-cis-benchmark
```

### Docker with Persistent Data

```bash
# Store scan results persistently
docker-compose up -d
# Results stored in ./data directory
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: harness-cis-dashboard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: harness-cis-dashboard
  template:
    metadata:
      labels:
        app: harness-cis-dashboard
    spec:
      containers:
      - name: dashboard
        image: harness-cis-benchmark:latest
        ports:
        - containerPort: 5000
        env:
        - name: HARNESS_API_KEY
          valueFrom:
            secretKeyRef:
              name: harness-credentials
              key: api-key
        - name: HARNESS_ACCOUNT_ID
          valueFrom:
            secretKeyRef:
              name: harness-credentials
              key: account-id
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: harness-cis-dashboard
spec:
  selector:
    app: harness-cis-dashboard
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

### AWS ECS Deployment

```json
{
  "family": "harness-cis-dashboard",
  "containerDefinitions": [
    {
      "name": "dashboard",
      "image": "harness-cis-benchmark:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "HARNESS_API_KEY",
          "value": "your-api-key"
        },
        {
          "name": "HARNESS_ACCOUNT_ID",
          "value": "your-account-id"
        }
      ]
    }
  ]
}
```

## Security Best Practices

### API Key Management

**Never commit API keys to version control!**

Use environment variables or secrets management:

```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id harness/api-key \
  --query SecretString \
  --output text

# HashiCorp Vault
vault kv get -field=api_key secret/harness

# Kubernetes Secrets
kubectl create secret generic harness-credentials \
  --from-literal=api-key=your_key \
  --from-literal=account-id=your_account
```

### Network Security

```nginx
# nginx.conf - Add SSL termination
server {
    listen 443 ssl http2;
    server_name dashboard.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://harness-cis-dashboard:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Resource Limits

Recommended container resources:
- **CPU**: 250m (minimum) - 500m (recommended)
- **Memory**: 256Mi (minimum) - 512Mi (recommended)
- **Storage**: 1GB for scan results

## Monitoring & Health Checks

### Health Endpoint

```bash
# Check if dashboard is healthy
curl http://localhost:5000/health

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "build_date": "2026-03-19",
  "has_results": true
}
```

### Logs

```bash
# Docker logs
docker logs harness-cis-agent -f

# Docker Compose logs
docker-compose logs -f

# Kubernetes logs
kubectl logs -f deployment/harness-cis-dashboard
```

### Metrics

Key metrics to monitor:
- Scan completion time (typically 10-30 seconds)
- Memory usage (should stay under 512MB)
- API error rate
- Dashboard response time

## Troubleshooting

### Common Issues

**Dashboard won't start:**
```bash
# Check if port 5000 is available
lsof -ti:5000

# Use different port
docker run -p 8080:5000 ...
```

**API errors:**
```bash
# Verify credentials
curl -H "x-api-key: $HARNESS_API_KEY" \
  https://app.harness.io/ng/api/users?accountIdentifier=$HARNESS_ACCOUNT_ID

# Check API key permissions
# Required: Account Viewer role or higher
```

**Scan takes too long:**
- Check network connectivity to Harness
- Verify delegate health
- Review scan timeout settings

**Memory issues:**
- Increase container memory limits
- Reduce concurrent scans
- Clear cached results

## API Reference

### Endpoints

**GET /** - Main dashboard UI

**GET /api/results** - Get cached scan results
```bash
curl http://localhost:5000/api/results
```

**GET /api/scan** - Trigger new scan
```bash
curl http://localhost:5000/api/scan
```

**GET /api/stats** - Get summary statistics
```bash
curl http://localhost:5000/api/stats
```

**GET /health** - Health check
```bash
curl http://localhost:5000/health
```

**GET /api/info** - Version and info
```bash
curl http://localhost:5000/api/info
```

## Upgrading

### Pull Latest Version

```bash
# Docker
docker pull harness-cis-benchmark:latest
docker-compose down
docker-compose up -d

# Git
git pull
docker-compose build
docker-compose up -d
```

### Version Pinning

```yaml
# docker-compose.yml
services:
  harness-cis-dashboard:
    image: harness-cis-benchmark:1.0.0  # Pin to specific version
```

## Customer Support

### Required Permissions

The Harness API key needs these permissions:
- ✅ View Users
- ✅ View User Groups
- ✅ View Roles
- ✅ View Resource Groups
- ✅ View Connectors
- ✅ View Secrets
- ✅ View Delegates
- ✅ View Pipelines
- ✅ View Templates
- ✅ View Policies

### Firewall Rules

Allow outbound HTTPS (443) to:
- `app.harness.io`
- `*.harness.io`

### Data Privacy

This agent:
- ✅ Does NOT store credentials
- ✅ Does NOT send data externally
- ✅ Runs entirely in customer's environment
- ✅ Only queries Harness APIs
- ✅ Results stay local

## Distribution

### Building the Agent

```bash
# Build Docker image
docker build -t harness-cis-benchmark:1.0.0 .

# Tag for distribution
docker tag harness-cis-benchmark:1.0.0 \
  your-registry/harness-cis-benchmark:1.0.0

# Push to registry
docker push your-registry/harness-cis-benchmark:1.0.0
```

### Create Release Package

```bash
# Create customer package
tar -czf harness-cis-agent-v1.0.0.tar.gz \
  dashboard.py \
  harness_api.py \
  harness_platform.py \
  main.py \
  models.py \
  constants.py \
  utils.py \
  requirements.txt \
  Dockerfile \
  docker-compose.yml \
  .env.example \
  templates/ \
  static/ \
  DEPLOYMENT.md \
  README.md
```

## License & Support

Include your licensing and support information here.

---

**Questions?** Contact your Harness representative or support team.
