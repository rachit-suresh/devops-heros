#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p evidence
exec > >(tee evidence/terraform.log) 2>&1
printf 'INFRA PROOF: LOCALSTACK ONLY, NO REAL AWS APPLY\n'
terraform -chdir=terraform init -input=false
terraform -chdir=terraform validate
# No plan/apply in the real-AWS directory: no AWS permission or paid usage.
docker run -d --name tracktonic-localstack -p 4566:4566 -e SERVICES=ec2 localstack/localstack:3.8
trap 'terraform -chdir=terraform-localstack destroy -auto-approve -input=false || true; docker rm -f tracktonic-localstack || true' EXIT
for i in $(seq 1 90); do
  if curl -fsS http://localhost:4566/_localstack/health | grep -q 'ec2'; then break; fi
  sleep 2
done
terraform -chdir=terraform-localstack init -input=false
terraform -chdir=terraform-localstack validate
terraform -chdir=terraform-localstack plan -out=local.tfplan -input=false
terraform -chdir=terraform-localstack apply -auto-approve -input=false local.tfplan
terraform -chdir=terraform-localstack output -json > evidence/localstack-outputs.json
terraform -chdir=terraform-localstack destroy -auto-approve -input=false
terraform -chdir=terraform-localstack state list > evidence/localstack-empty-state.txt
printf 'LOCALSTACK lifecycle complete. Real AWS VPC/EKS not provisioned.\n'
