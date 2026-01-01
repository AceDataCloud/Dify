#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

kubectl apply -f "${SCRIPT_DIR}/production/secret"
kubectl apply -f "${SCRIPT_DIR}/production/configmap"
kubectl apply -f "${SCRIPT_DIR}/production/service"
kubectl apply -f "${SCRIPT_DIR}/production/pvc"
kubectl apply -f "${SCRIPT_DIR}/production/statefulset"
kubectl apply -f "${SCRIPT_DIR}/production/deployment"

if [ -n "${BUILD_NUMBER:-}" ]; then
  kubectl -n acedatacloud set image statefulset/platform-service-dify-api \
    platform-service-dify-api="ghcr.io/acedatacloud/platform-service-dify-api:${BUILD_NUMBER}"

  kubectl -n acedatacloud set image statefulset/platform-service-dify-worker \
    platform-service-dify-worker="ghcr.io/acedatacloud/platform-service-dify-api:${BUILD_NUMBER}"

  kubectl -n acedatacloud set image deployment/platform-service-dify-worker-beat \
    platform-service-dify-worker-beat="ghcr.io/acedatacloud/platform-service-dify-api:${BUILD_NUMBER}"

  kubectl -n acedatacloud set image deployment/platform-service-dify-web \
    platform-service-dify-web="ghcr.io/acedatacloud/platform-service-dify-web:${BUILD_NUMBER}"
fi
