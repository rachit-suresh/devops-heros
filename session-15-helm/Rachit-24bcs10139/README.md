# Session 15 - Helm Mini-Project: notes-chart (Rachit, 24BCS10139)

Built a Helm chart (`notes-chart`) from scratch and ran the full release lifecycle on minikube (Kubernetes v1.37) with Helm v4.3.0.

## Chart
`notes-chart/` with Chart.yaml, values.yaml, values-prod.yaml and templates for a Deployment, Service (NodePort) and ConfigMap.

## Lifecycle captured
1. `helm lint` - chart passes with no errors.
2. `helm template` - renders Deployment/Service/ConfigMap manifests from values.
3. `helm install notes-dev` with dev values - 1 pod Running, NodePort 30090, ConfigMap created.
4. `helm upgrade` with `values-prod.yaml` - scales to 3 replicas (revision 2).
5. `helm history` - revisions 1 and 2.
6. Bad upgrade on purpose (`nginx:broken-tag-does-not-exist`, revision 3) - new pod stuck pulling the missing image.
7. `helm rollback notes-dev 2` - rollout back to the good revision, 3/3 Running; history shows revision 4 = "Rollback to 2".
8. `helm uninstall notes-dev` - release and resources removed.

## Screenshots
- `Screenshots/01-chart-lint.png` - chart layout + lint
- `Screenshots/02-template.png` - helm template output
- `Screenshots/03-install-upgrade.png` - install (dev) then upgrade to prod values
- `Screenshots/04-rollback.png` - bad upgrade + rollback to revision 2
- `Screenshots/05-cleanup.png` - uninstall

## Evidence
- `evidence/session-15.log` - full terminal capture
