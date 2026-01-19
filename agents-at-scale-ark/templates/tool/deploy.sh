#!/bin/bash
set -e

cd "$(dirname "$0")"

docker build -t tool:latest .
# Load image into cluster - adjust command based on your cluster type
# kind load docker-image tool:latest --name cluster-name
# eval $(minikube docker-env) && docker build -t tool:latest .
kubectl apply -k deployment/