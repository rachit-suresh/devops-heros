# Session 17 - DevSecOps Pipeline: hey-cicd (Rachit, 24BCS10139)

Full DevSecOps CI/CD pipeline in GitHub Actions for the `hey-cicd` Flask demo app, with security gates and a container deploy to an ephemeral kind cluster.

Green run: https://github.com/rachit-suresh/devops-heros/actions/runs/37580263897
Workflow: `.github/workflows/session17-devsecops.yml` (on branch `session-17-devsecops-rachit-24bcs10139`).

## Pipeline stages (all green)
1. **Unit Tests (pytest)** - app tests pass.
2. **SAST - CodeQL** - static analysis of the Python code.
3. **SCA - pip-audit** - dependency vulnerability audit.
4. **Docker Build** - builds `hey-cicd:<commit-sha>`.
5. **Image Scan - Trivy** - HIGH,CRITICAL severity scan of the built image.
6. **Push Image to GHCR** - pushes to `ghcr.io/rachit-suresh/hey-cicd` (digest sha256:fff74ec... on the green run). The instructor's demo pointed at her own Docker Hub; this version uses GHCR with the workflow's `GITHUB_TOKEN` instead.
7. **Deploy to ephemeral kind cluster** - kind-action spins up a throwaway cluster, loads the image, applies `k8s/deployment.yaml` + `k8s/service.yaml`, rollout verified (`deployment "session17-python" successfully rolled out`).

## Fixes made while getting to green
- Trivy action pinned to a full version tag (`v0.36.0`).
- kind cluster name aligned (`cluster_name: kind`) so `kind load` and the deploy target the same cluster.

## Screenshots
- `Screenshots/01-pipeline-jobs.png` - all 7 jobs green on run 37580263897
- `Screenshots/02-ghcr-push-deploy.png` - GHCR push digest + kind deploy/rollout log lines

## Evidence
- `evidence/s17-runview.txt` - gh run view output
- `evidence/s17-push-deploy.txt` - push + deploy log excerpts
