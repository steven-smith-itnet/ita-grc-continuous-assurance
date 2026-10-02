"""Project 02: configuration baseline evaluation and drift detection across providers.

Provider-native API responses are normalized into four canonical storage settings.
Every adapter returns None when the native response cannot establish the value, so
an absent or ambiguous field becomes UNKNOWN rather than PASS.
"""
from collections import Counter

from .engine import STATES, timestamp

SETTINGS = ("public_access_prevented", "identity_only_access", "versioning_enabled", "customer_managed_key")
AWS_PAB = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")


def _aws(raw):
    """Combine s3api and kms responses: get-public-access-block, get-bucket-ownership-controls,
    get-bucket-versioning, get-bucket-encryption and kms describe-key."""
    out = dict.fromkeys(SETTINGS)
    pab = raw.get("GetPublicAccessBlock")
    if isinstance(pab, dict):
        values = [pab.get("PublicAccessBlockConfiguration", {}).get(f) for f in AWS_PAB]
        if all(type(v) is bool for v in values):
            out["public_access_prevented"] = all(values)
    ownership = raw.get("GetBucketOwnershipControls")
    if isinstance(ownership, dict):
        rules = ownership.get("OwnershipControls", {}).get("Rules")
        if isinstance(rules, list) and rules:
            out["identity_only_access"] = rules[0].get("ObjectOwnership") == "BucketOwnerEnforced"
    versioning = raw.get("GetBucketVersioning")
    if isinstance(versioning, dict):
        # A bucket whose versioning was never configured returns no Status. That is a real "off".
        out["versioning_enabled"] = versioning.get("Status") == "Enabled"
    encryption = raw.get("GetBucketEncryption")
    if isinstance(encryption, dict):
        rules = encryption.get("ServerSideEncryptionConfiguration", {}).get("Rules")
        default = rules[0].get("ApplyServerSideEncryptionByDefault", {}) if isinstance(rules, list) and rules else {}
        algorithm = default.get("SSEAlgorithm")
        if algorithm == "AES256":
            out["customer_managed_key"] = False
        elif algorithm in ("aws:kms", "aws:kms:dsse"):
            manager = (raw.get("DescribeKey") or {}).get("KeyMetadata", {}).get("KeyManager")
            if not default.get("KMSMasterKeyID"):
                out["customer_managed_key"] = False  # falls back to the AWS managed aws/s3 key
            elif manager in ("CUSTOMER", "AWS"):
                out["customer_managed_key"] = manager == "CUSTOMER"
    return out


def _azure(raw):
    """Combine az storage account show and az storage account blob-service-properties show."""
    out = dict.fromkeys(SETTINGS)
    account = raw.get("storageAccount")
    if isinstance(account, dict):
        public = account.get("allowBlobPublicAccess")
        if type(public) is bool:
            out["public_access_prevented"] = not public
        if "allowSharedKeyAccess" in account:
            # Microsoft documents a null value as equivalent to true: shared key authorization is allowed.
            out["identity_only_access"] = account["allowSharedKeyAccess"] is False
        source = (account.get("encryption") or {}).get("keySource")
        if source in ("Microsoft.Keyvault", "Microsoft.Storage"):
            out["customer_managed_key"] = source == "Microsoft.Keyvault"
    blob = raw.get("blobServiceProperties")
    if isinstance(blob, dict) and type(blob.get("isVersioningEnabled")) is bool:
        out["versioning_enabled"] = blob["isVersioningEnabled"]
    return out


def _gcp(raw):
    """Cloud Storage JSON API bucket resource. Absent fields stay unknown because a
    partial-response projection also omits them."""
    out = dict.fromkeys(SETTINGS)
    iam = raw.get("iamConfiguration")
    if isinstance(iam, dict):
        # 'inherited' depends on an organization policy that this snapshot does not include.
        if iam.get("publicAccessPrevention") == "enforced":
            out["public_access_prevented"] = True
        ubla = (iam.get("uniformBucketLevelAccess") or {}).get("enabled")
        if type(ubla) is bool:
            out["identity_only_access"] = ubla
    versioning = raw.get("versioning")
    if isinstance(versioning, dict) and type(versioning.get("enabled")) is bool:
        out["versioning_enabled"] = versioning["enabled"]
    encryption = raw.get("encryption")
    if isinstance(encryption, dict):
        out["customer_managed_key"] = bool(encryption.get("defaultKmsKeyName"))
    return out


ADAPTERS = {"aws": _aws, "azure": _azure, "gcp": _gcp}


def normalize(provider, raw):
    if provider not in ADAPTERS:
        raise ValueError("unsupported provider")
    return ADAPTERS[provider](raw if isinstance(raw, dict) else {})


def _applies(setting, resource):
    return all(resource.get(k) in v for k, v in setting.get("applies", {}).items())


def evaluate(baseline, resources, before, after, changes):
    """Return baseline rows for the latest snapshot and drift events between the two snapshots."""
    t0, t1 = timestamp(before["collected_at"]), timestamp(after["collected_at"])
    if t1 <= t0:
        raise ValueError("snapshots must be in time order")
    rows, events = [], []
    for resource in sorted(resources["resources"], key=lambda r: r["id"]):
        rid, provider = resource["id"], resource["provider"]
        now = normalize(provider, after["resources"].get(rid, {}))
        then = normalize(provider, before["resources"].get(rid, {}))
        for setting in baseline["settings"]:
            sid, expected = setting["id"], setting["expected"]
            row = {"resource_id": rid, "provider": provider, "setting": sid, "severity": setting["severity"],
                   "observed": now[sid], "expected": expected}
            if not _applies(setting, resource):
                row.update(status="NOT_APPLICABLE", reasons=["outside the setting's documented population"])
                rows.append(row)
                continue
            if rid not in after["resources"]:
                row.update(status="UNKNOWN", reasons=["resource missing from the latest snapshot"])
            elif now[sid] is None:
                row.update(status="UNKNOWN", reasons=["native response does not establish this setting: " + setting["native"][provider]])
            elif now[sid] == expected:
                row.update(status="PASS", reasons=["matches baseline: " + setting["native"][provider]])
            else:
                row.update(status="FAIL", reasons=[f"observed {now[sid]}, baseline expects {expected}: " + setting["native"][provider]])
            rows.append(row)
            if then[sid] == now[sid]:
                continue
            event = {"resource_id": rid, "provider": provider, "setting": sid, "before": then[sid], "after": now[sid]}
            if then[sid] is None or now[sid] is None:
                event.update(direction="undetermined", change_id=None, status="UNKNOWN",
                             reasons=["value not established in one snapshot; drift cannot be classified"])
            else:
                ticket = next((c for c in changes["changes"] if c["resource_id"] == rid and c["setting"] == sid
                               and c.get("status") == "approved"
                               and t0 <= timestamp(c["window_start"]) <= timestamp(c["window_end"]) <= t1), None)
                direction = "toward baseline" if now[sid] == expected else "away from baseline"
                event.update(direction=direction, change_id=ticket["change_id"] if ticket else None,
                             status="PASS" if ticket else "FAIL",
                             reasons=[f"authorized by {ticket['change_id']}" if ticket else
                                      "no approved change covers this setting in the window between snapshots"])
                if ticket and direction == "away from baseline":
                    event["reasons"].append("authorized change still leaves the resource off baseline; an exception is required")
            events.append(event)
    return rows, events


def counts(rows):
    tally = Counter(r["status"] for r in rows)
    return {s: tally[s] for s in STATES}
