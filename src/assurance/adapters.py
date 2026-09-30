"""Narrow provider-schema examples. Unknown fields never become a passing fact.

AWS input: s3api get-public-access-block JSON.
Azure input: az storage account show JSON.
GCP input: Cloud Storage JSON API bucket resource, not gcloud display YAML.
These adapters prove one explicit resource-level prevention baseline, not effective access.
"""


def explicit_public_prevention(provider, raw):
    if provider == "aws":
        fields = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
        config = raw.get("PublicAccessBlockConfiguration", {})
        values = [config.get(f) for f in fields]
        if any(type(v) is not bool for v in values):
            return None
        return all(values)
    if provider == "azure":
        value = raw.get("allowBlobPublicAccess")
        return not value if type(value) is bool else None
    if provider == "gcp":
        value = raw.get("iamConfiguration", {}).get("publicAccessPrevention")
        # 'inherited' requires an organization-policy query and cannot establish this baseline.
        return True if value == "enforced" else None
    raise ValueError("unsupported provider")
