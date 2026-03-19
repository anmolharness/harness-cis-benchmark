#!/bin/bash
# Build and package Harness CIS Benchmark Agent for customer distribution

set -e

VERSION="1.0.0"
BUILD_DATE=$(date +%Y-%m-%d)

echo "🔨 Building Harness CIS Benchmark Agent v${VERSION}..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t harness-cis-benchmark:${VERSION} .
docker tag harness-cis-benchmark:${VERSION} harness-cis-benchmark:latest

echo "✅ Docker image built: harness-cis-benchmark:${VERSION}"

# Create distribution package
echo "📦 Creating distribution package..."
mkdir -p dist

tar -czf dist/harness-cis-agent-v${VERSION}.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='dist' \
  --exclude='data' \
  --exclude='*.pyc' \
  --exclude='results.*' \
  --exclude='.env' \
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
  .dockerignore \
  .env.example \
  templates/ \
  static/ \
  CUSTOMER_README.md \
  DEPLOYMENT.md

echo "✅ Package created: dist/harness-cis-agent-v${VERSION}.tar.gz"

# Save Docker image
echo "💾 Saving Docker image..."
docker save harness-cis-benchmark:${VERSION} | gzip > dist/harness-cis-agent-docker-v${VERSION}.tar.gz

echo "✅ Docker image saved: dist/harness-cis-agent-docker-v${VERSION}.tar.gz"

# Create checksums
echo "🔐 Creating checksums..."
cd dist
sha256sum harness-cis-agent-v${VERSION}.tar.gz > harness-cis-agent-v${VERSION}.tar.gz.sha256
sha256sum harness-cis-agent-docker-v${VERSION}.tar.gz > harness-cis-agent-docker-v${VERSION}.tar.gz.sha256
cd ..

echo ""
echo "✨ Build complete!"
echo ""
echo "📦 Distribution files in dist/:"
ls -lh dist/
echo ""
echo "📝 Next steps:"
echo "1. Test the package: tar -xzf dist/harness-cis-agent-v${VERSION}.tar.gz"
echo "2. Load Docker image: docker load < dist/harness-cis-agent-docker-v${VERSION}.tar.gz"
echo "3. Distribute to customers"
