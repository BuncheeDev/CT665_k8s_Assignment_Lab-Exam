#!/usr/bin/env bash
set -euo pipefail

echo "=== 1. Checking 3-Node Kubernetes Cluster ==="
kubectl get nodes -o wide

echo "=== 2. Enabling NGINX Ingress Controller ==="
kubectl label node minikube minikube.k8s.io/primary=true --overwrite
minikube addons enable ingress
kubectl rollout status deployment/ingress-nginx-controller -n ingress-nginx --timeout=180s

echo "=== 3. Building Docker Images ==="
docker build -t portal-712:v1 ./portal-712
docker build -t app-research:v1 ./app-research
docker build -t api-712:v1 ./api-712
docker build -t admin-712:v1 ./admin-712

echo "=== 4. Loading Images into All 3 Minikube Nodes ==="
minikube image load portal-712:v1
minikube image load app-research:v1
minikube image load api-712:v1
minikube image load admin-712:v1

echo "=== 5. Applying Kubernetes Manifests ==="
kubectl apply -f k8s/rbac-configmap.yaml
kubectl apply -f k8s/portal-712.yaml
kubectl apply -f k8s/app-research.yaml
kubectl apply -f k8s/api-712.yaml
kubectl apply -f k8s/admin-712.yaml
kubectl apply -f k8s/ingress.yaml

echo "=== 6. Waiting for Deployments ==="
kubectl rollout status deployment/portal-712 --timeout=120s
kubectl rollout status deployment/app-research --timeout=120s
kubectl rollout status deployment/api-712 --timeout=120s
kubectl rollout status deployment/admin-712 --timeout=120s

echo "=== 7. Updating /etc/hosts ==="
MINIKUBE_IP=$(minikube ip)
sudo sed -i '/iam-712\.com\|id-712\.com/d' /etc/hosts
echo "${MINIKUBE_IP} www.iam-712.com www.id-712.com admin.iam-712.com" | sudo tee -a /etc/hosts

echo "=== 8. Deployment Summary ==="
kubectl get nodes,deployments,pods,svc,ingress -o wide
