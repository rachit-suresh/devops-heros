# Session 13 - Storage, HPA and Probes (Rachit, 24BCS10139)

Mini-project on minikube (Kubernetes v1.37): the official `session-13-storage-hpa-probes/mini-project` manifests (namespace production-webapp, PVC, Deployment web-app, Service, HPA 2-5 replicas at 50% CPU).

## What was demonstrated
1. **Setup:** namespace, PVC `web-data`, deployment, service and HPA created.
2. **Storage persistence (Task 1):** wrote a file containing "Student: Rachit 24BCS10139" into the PVC-mounted path inside a pod, deleted the pod, waited for the rollout, then read the same file from the new pod - contents survived.
3. **Service verification (Task 2):** ClusterIP service `web-service` serves the nginx welcome page (fetched over the service).
4. **Probes:** readiness and liveness probe config dumped from the live pod spec.
5. **HPA scaling (Task 3):** three busybox load generators drove CPU from 1% to 66% of the 50% target; under sustained load the HPA scaled the deployment from 2 to 4 replicas (target 46%/50%, `kubectl top` shows all four web-app pods plus the three generators). A fortio burst (30 connections) was also run against the service.

## Screenshots
- `Screenshots/01-setup.png` - namespace/PVC/deployment/service/HPA creation
- `Screenshots/02-persistence-service.png` - file survives pod deletion; service HTML
- `Screenshots/03-probes.png` - HPA created + probe config proof
- `Screenshots/04-spike-ramp.png` - CPU ramp 1% -> 27% -> 66% under 3 load generators
- `Screenshots/05-scaleout.png` - HPA at 4 replicas under sustained load
- `Screenshots/06-final.png` - final state

## Evidence
- `evidence/session-13.log` - full terminal capture (including the metrics-server fix and both load runs)

Note: the run happened inside a GitHub Codespace, which blocks pod/node DNS and node image pulls; a host-side DNS forwarder and `minikube image load` were used. Cluster mechanics are unchanged.
