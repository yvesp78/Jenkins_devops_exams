#!/bin/bash
set -e

### VARIABLES À MODIFIER ###
APP_DIR="app"                       
DOCKER_USER="monuser"               
IMAGE_TAG="1.0.0"
HELM_CHART_DIR="helm-chart"         
JENKINS_USER="jenkins"
NAMESPACES=("dev" "qa" "staging" "prod")
#################################

# === Vérification Git ===
echo "=== Vérification installation Git ==="
if ! command -v git &> /dev/null; then
  echo "Git non installé. Installation..."
  apt-get update -y
  apt-get install -y git
  echo "Git installé ✅"
else
  echo "Git déjà installé ✅"
fi

# === Vérification Docker ===
echo "=== Vérification installation Docker ==="
if ! command -v docker &> /dev/null; then
  echo "Docker non installé. Installation..."
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release
  mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  echo "Docker installé ✅"
else
  echo "Docker déjà installé ✅"
fi

# === Vérification k3s ===
echo "=== Vérification installation Kubernetes (k3s) ==="
if ! command -v k3s &> /dev/null; then
  echo "k3s non installé. Installation..."
  curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
else
  echo "k3s déjà installé ✅"
fi

# Vérification nodes
echo "=== Vérification des nodes Kubernetes ==="
k3s kubectl get nodes

# === Vérification Helm ===
echo "=== Vérification installation Helm ==="
if ! command -v helm &> /dev/null; then
  echo "Helm non installé. Installation..."
  curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
  chmod 700 get_helm.sh
  ./get_helm.sh
else
  echo "Helm déjà installé ✅"
fi

# === Création des namespaces Kubernetes ===
for ns in "${NAMESPACES[@]}"; do
  if ! k3s kubectl get ns "$ns" &>/dev/null; then
    k3s kubectl create namespace "$ns"
    echo "Namespace $ns créé ✅"
  else
    echo "Namespace $ns existe déjà ✅"
  fi
done

echo "✅ Script d'environnement prêt. Les étapes Docker Compose, Helm et health check seront gérées dans Jenkins."
