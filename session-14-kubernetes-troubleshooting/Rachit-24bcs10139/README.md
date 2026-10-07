# Session 14 - Kubernetes Troubleshooting (Rachit, 24BCS10139)

Troubleshooting challenge run on minikube (Kubernetes v1.37) inside a GitHub Codespace.

## What was done
1. Deployed `troubleshooting-app` (2 replicas, nginx:1.27) and verified pods, deployment, service and endpoints.
2. Diagnosed a broken pod (`project-broken-pod`) stuck because its image tag did not exist, answered the challenge questions from live `kubectl` output, then fixed it by patching the pod to a valid tag.
3. Broke the service selector on purpose, observed empty endpoints, then fixed the selector and confirmed endpoints recovered.
4. Final checklist: all pods Running, service endpoints present.

## Diagnosis Q&A (from the live cluster)
- Q1 status: ContainerCreating (Events show the image pull failing)
- Q2 error: `Failed to pull image nginx:this-tag-does-not-exist` (tag does not exist on Docker Hub)
- Q3 command: `kubectl describe pod project-broken-pod` (Events section)
- Q4 wrong with image: the tag `this-tag-does-not-exist` does not exist for nginx
- Q5 fix: point the pod at an existing tag, e.g. nginx:1.27
- Service with broken selector: `kubectl get endpoints` returns `<none>` because no pods match; fixing the selector back to `app=troubleshooting-app` restores the endpoints.

## Screenshots
- `Screenshots/01-deploy-verify.png` - deployment, pods, service verification
- `Screenshots/02-broken-pod-diagnosis.png` - broken pod events + Q&A + fix
- `Screenshots/03-selector-endpoints.png` - selector break, `<none>` endpoints, fix
- `Screenshots/04-final-checklist.png` - final healthy state

## Evidence
- `evidence/session-14.log` - full terminal capture of the whole run
