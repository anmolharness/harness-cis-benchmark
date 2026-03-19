#!/bin/bash
# Deploy Harness CIS Benchmark Agent to Kubernetes

set -e

echo "🚀 Deploying Harness CIS Benchmark Agent to Kubernetes..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Create .env with HARNESS_API_KEY and HARNESS_ACCOUNT_ID"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required variables
if [ -z "$HARNESS_API_KEY" ] || [ -z "$HARNESS_ACCOUNT_ID" ]; then
    echo "❌ Error: HARNESS_API_KEY and HARNESS_ACCOUNT_ID must be set in .env"
    exit 1
fi

echo "✅ Environment variables loaded"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Create secret with credentials
echo "🔐 Creating secret..."
envsubst < k8s/secret.yaml | kubectl apply -f -

# Deploy application
echo "🚀 Deploying application..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Optional: Deploy ingress if you have ingress controller
# kubectl apply -f k8s/ingress.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Checking status..."
kubectl get pods -n harness-cis -w &
WATCH_PID=$!
sleep 10
kill $WATCH_PID 2>/dev/null || true

echo ""
echo "🌐 Access the dashboard:"
echo ""
echo "Option 1 - Port Forward:"
echo "  kubectl port-forward -n harness-cis svc/harness-cis-dashboard 5000:5000"
echo "  Then open: http://localhost:5000"
echo ""
echo "Option 2 - NodePort:"
echo "  http://<node-ip>:30500"
echo ""
echo "📝 Useful commands:"
echo "  kubectl logs -n harness-cis -l app=harness-cis-dashboard -f"
echo "  kubectl get all -n harness-cis"
echo "  kubectl delete namespace harness-cis  # To remove everything"
