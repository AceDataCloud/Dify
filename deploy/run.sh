#!/bin/sh
set -eu

: "${BUILD_NUMBER:?BUILD_NUMBER is required}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

kubectl apply -f "$SCRIPT_DIR/production/configmap"
kubectl apply -f "$SCRIPT_DIR/production/service"
for manifest in "$SCRIPT_DIR"/production/deployment/*.yml; do
  sed 's/\${TAG}/'"$BUILD_NUMBER"'/g' "$manifest" | kubectl apply -f -
done
