#!/bin/sh
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "${APPLY_SECRETS:-false}" = "true" ]; then
  kubectl apply -f "${SCRIPT_DIR}/production/secret"
fi

if ! kubectl -n acedatacloud get secret dify >/dev/null 2>&1; then
  echo "Missing required secret: dify (namespace: acedatacloud)"
  echo "Create it manually, or set APPLY_SECRETS=true after replacing placeholders in deploy/production/secret/dify.yml"
  exit 1
fi

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
