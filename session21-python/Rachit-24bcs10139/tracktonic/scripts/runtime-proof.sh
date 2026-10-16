#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p evidence
exec > >(tee evidence/runtime.log) 2>&1
trap 'kubectl get pods -A -o wide || true; kubectl get events -n tracktonic --sort-by=.lastTimestamp | tail -30 || true' ERR
printf 'TrackTonic runtime proof | UTC '; date -u --iso-8601=seconds
printf 'Source commit: '; git rev-parse HEAD
# Reuse the already scanned source images for Compose.
cat > /tmp/compose-proof.yml <<YAML
services:
  backend:
    image: ${BACKEND_IMAGE}:${IMAGE_TAG}
  frontend:
    image: ${FRONTEND_IMAGE}:${IMAGE_TAG}
YAML
docker compose -f docker-compose.yml -f /tmp/compose-proof.yml up -d --no-build --wait --wait-timeout 180
docker compose ps | tee evidence/compose.txt
curl -fsS http://localhost:8000/ready
python -m pip install --quiet playwright
python -m playwright install --with-deps chromium
APP_URL=http://localhost:3000 OUTPUT_PREFIX=compose python scripts/browser-proof.py
# A throwaway local Kubernetes cluster, no AWS calls.
curl -fsSL https://kind.sigs.k8s.io/dl/v0.31.0/kind-linux-amd64 -o /tmp/kind
sudo install -m 0755 /tmp/kind /usr/local/bin/kind
cat > /tmp/kind.yaml <<YAML
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 80
        hostPort: 8080
        protocol: TCP
YAML
kind create cluster --name tracktonic --config /tmp/kind.yaml --wait 180s
kind load docker-image "${BACKEND_IMAGE}:${IMAGE_TAG}" "${FRONTEND_IMAGE}:${IMAGE_TAG}" --name tracktonic
kubectl apply -f k8s/namespace.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=240s
# The controller pod reports ready before its admission webhook answers;
# helm's Ingress apply fails against a half-up webhook. Wait for the endpoint.
for i in $(seq 1 60); do
  if kubectl get endpointslices -n ingress-nginx -l kubernetes.io/service-name=ingress-nginx-controller-admission -o jsonpath='{.items[*].endpoints[*].conditions.ready}' 2>/dev/null | grep -q true; then
    break
  fi
  sleep 3
done
# Admission jobs can vanish before this wait (ttlSecondsAfterFinished), so
# never fail here - the helm retry below is the real guard.
kubectl wait --namespace ingress-nginx --for=condition=complete job/ingress-nginx-admission-create job/ingress-nginx-admission-patch --timeout=180s || true
helm lint helm/tracktonic
# The admission webhook can refuse connections for a few seconds after the
# controller pod reports Ready; retry instead of racing it.
helm_ok=0
for attempt in 1 2 3 4 5; do
  if helm upgrade --install tracktonic helm/tracktonic -n tracktonic --create-namespace --set backend.image="$BACKEND_IMAGE" --set backend.tag="$IMAGE_TAG" --set frontend.image="$FRONTEND_IMAGE" --set frontend.tag="$IMAGE_TAG" --wait --timeout 6m; then
    helm_ok=1
    break
  fi
  echo "helm install attempt $attempt failed; retrying in 15s"
  sleep 15
done
[ "$helm_ok" = 1 ]
kubectl get pods -n tracktonic -o wide | tee evidence/pods.txt
kubectl get svc -n tracktonic | tee evidence/services.txt
helm list -n tracktonic | tee evidence/helm.txt
kubectl get ingress,hpa -n tracktonic | tee evidence/ingress-hpa.txt
kubectl exec -n tracktonic deploy/postgres -- psql -U tracktonic -d tracktonic -c '\dt' | tee evidence/postgres.txt
curl -fsS -H 'Host: tracktonic.local' http://localhost:8080/ > /dev/null
# The frontend answers before ingress endpoints for the API sync; gate on the
# API path too so the browser proof never loads a page whose fetch 503s.
for i in $(seq 1 30); do
  if curl -fsS -H 'Host: tracktonic.local' http://localhost:8080/api/albums > /dev/null; then
    break
  fi
  sleep 2
done
kubectl port-forward -n tracktonic svc/grafana 3001:3000 > /tmp/grafana-forward.log 2>&1 &
GRAFANA_PID=$!
kubectl port-forward -n tracktonic svc/prometheus-server 9090:9090 > /tmp/prom-forward.log 2>&1 &
PROM_PID=$!
APP_URL=http://localhost:8080 OUTPUT_PREFIX=kubernetes INGRESS_HOST=tracktonic.local python scripts/browser-proof.py
# Send sustained real requests so a populated graph has multiple scrape points.
for i in $(seq 1 45); do curl -fsS -H 'Host: tracktonic.local' http://localhost:8080/api/albums >/dev/null; sleep 1; done
MONITORING_PROOF=1 python scripts/browser-proof.py
curl -fsS 'http://localhost:9090/api/v1/targets' | python -m json.tool > evidence/prometheus-targets.json
curl -fsS 'http://localhost:9090/api/v1/query?query=sum%28tracktonic_http_requests_total%29' | python -m json.tool > evidence/metric-query.json
# Deliberately break only an isolated Service, inspect its empty EndpointSlice, repair.
kubectl expose deployment backend -n tracktonic --name=broken-service --port=8000
kubectl patch svc broken-service -n tracktonic -p '{"spec":{"selector":{"app":"wrong-label"}}}'
kubectl get endpointslice -n tracktonic -l kubernetes.io/service-name=broken-service -o yaml > evidence/service-broken.yaml
kubectl patch svc broken-service -n tracktonic -p '{"spec":{"selector":{"app":"backend"}}}'
kubectl get endpointslice -n tracktonic -l kubernetes.io/service-name=broken-service -o yaml > evidence/service-repaired.yaml
kubectl delete svc broken-service -n tracktonic
kill "$GRAFANA_PID" "$PROM_PID" || true
printf 'Runtime proof completed | UTC '; date -u --iso-8601=seconds
