#!/bin/sh
set -eu

: "${BUILD_NUMBER:?BUILD_NUMBER is required}"
NAMESPACE="${NAMESPACE:-acedatacloud}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for resource in "secret/dify" "pvc/dify" "secret/pgsql-qcloud" "secret/redis-qcloud" "secret/vdb-qcloud" "secret/docker-registry"; do
  kubectl -n "$NAMESPACE" get "$resource" >/dev/null
 done

checksum=$(sha256sum "$SCRIPT_DIR/production/configmap/dify-env.yml" | awk '{print $1}')
for deployment in dify-api dify-worker dify-worker-beat dify-web dify-plugin-daemon dify-nginx dify-sandbox; do
  kubectl -n "$NAMESPACE" patch deployment "$deployment" \
    -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"dify-env/checksum\":\"$checksum\"}}}}}"
  kubectl -n "$NAMESPACE" rollout status "deployment/$deployment" --timeout=15m
done

expected_api="ghcr.io/acedatacloud/dify-api:$BUILD_NUMBER"
expected_web="ghcr.io/acedatacloud/dify-web:$BUILD_NUMBER"
test "$(kubectl -n "$NAMESPACE" get deployment dify-api -o jsonpath='{.spec.template.spec.containers[0].image}')" = "$expected_api"
test "$(kubectl -n "$NAMESPACE" get deployment dify-worker -o jsonpath='{.spec.template.spec.containers[0].image}')" = "$expected_api"
test "$(kubectl -n "$NAMESPACE" get deployment dify-worker-beat -o jsonpath='{.spec.template.spec.containers[0].image}')" = "$expected_api"
test "$(kubectl -n "$NAMESPACE" get deployment dify-web -o jsonpath='{.spec.template.spec.containers[0].image}')" = "$expected_web"
