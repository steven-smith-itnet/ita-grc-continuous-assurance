# Cloud templates and validation boundary

These are pilot building blocks. None has been applied to a cloud account by this project. They do not configure a full landing zone, full logging, private endpoint DNS, customer-managed-key lifecycle, organization inventory or an immutable evidence archive.

Use an approved sandbox and review current provider schemas before running native validation. Validation and plans are not deployment evidence.

```bash
aws cloudformation validate-template --template-body file://infra/aws/storage.yaml
az bicep build --file infra/azure/storage.bicep
terraform -chdir=infra/gcp init -backend=false
terraform -chdir=infra/gcp validate
```

AWS validation calls an AWS API and needs credentials. Bicep build is local after installing Bicep. Terraform init downloads provider plugins. A provider lock file is included from local validation with Google provider 7.46.1. Review provider changes and regenerate the lock deliberately when upgrading.

Before apply: select a region, budget, resource owner and teardown plan, review change set/what-if/plan and verify identities. The Azure baseline denies public networking and needs additional private connectivity for data-plane use. The AWS bucket retains data on stack deletion. The GCP bucket refuses force deletion. Do not bypass retention or legal holds to simplify cleanup.
