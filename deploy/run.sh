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
kubectl apply -f "${SCRIPT_DIR}/production/statefulset"
kubectl apply -f "${SCRIPT_DIR}/production/deployment"

if [ -n "${BUILD_NUMBER:-}" ]; then
  kubectl -n acedatacloud set image statefulset/dify-api \
    dify-api="ghcr.io/acedatacloud/dify-api:${BUILD_NUMBER}"

  kubectl -n acedatacloud set image statefulset/dify-worker \
    dify-worker="ghcr.io/acedatacloud/dify-api:${BUILD_NUMBER}"

  kubectl -n acedatacloud set image deployment/dify-worker-beat \
    dify-worker-beat="ghcr.io/acedatacloud/dify-api:${BUILD_NUMBER}"

  kubectl -n acedatacloud set image deployment/dify-web \
    dify-web="ghcr.io/acedatacloud/dify-web:${BUILD_NUMBER}"
fi
