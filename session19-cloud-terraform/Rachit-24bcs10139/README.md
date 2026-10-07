# Session 19 - Terraform VPC Mini-Project (Rachit, 24BCS10139)

Built the official `08-mini-project` VPC stack (VPC, public subnet, internet gateway, route table + association, security group) against LocalStack inside a GitHub Codespace. LocalStack emulates the AWS EC2 API locally; the Terraform workflow and resources are the same as on real AWS.

## Changes vs the official lab files (in `terraform/`)
- Added `zz-localstack.tf`: AWS provider pointed at LocalStack endpoints (dummy credentials). The provider block in `versions.tf` was removed so only one AWS provider configuration exists.

## Results
- `terraform validate` -> "Success! The configuration is valid."
- `terraform apply` -> "Apply complete! Resources: 6 added, 0 changed, 0 destroyed."
- Outputs: vpc_id = vpc-f2d2c4ed9e53b3c11 (10.20.0.0/16), subnet_id = subnet-d1fb6abaf0810fb8e, security_group_id = sg-dd9c42c6d20ef8970.
- `terraform state list` shows all 6 resources: aws_vpc.main, aws_subnet.public, aws_internet_gateway.main, aws_route_table.public, aws_route_table_association.public, aws_security_group.web.
- Verified through the LocalStack EC2 API: describe-vpcs / describe-subnets / describe-route-tables / describe-security-groups return the created resources.

## Screenshots
- `Screenshots/01-init-validate.png` - init + validate
- `Screenshots/02-apply.png` - apply complete (6 added)
- `Screenshots/03-verify.png` - outputs, state list, EC2 API verification

## Evidence
- `evidence/session-19.log` - full terminal capture
- `terraform/` - the exact configuration applied
