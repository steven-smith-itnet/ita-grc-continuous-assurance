"""Project 01: control automation use cases.

Each function derives a control result from source-system records, such as HR,
identity-provider, cloud API, CI/CD, backup and scanner exports. The base lab
evaluates supplied booleans. These use cases compute those facts from the
records that produce them.

Rules shared by every use case:
- A missing, malformed or uncorrelated input produces UNKNOWN, never PASS.
- A proven failure is reported as FAIL even when another input is missing.
- Entities outside the documented population are reported as NOT_APPLICABLE
  with a reason, so the denominator stays visible.
"""
from collections import Counter

from .engine import STATES, timestamp


def _time(value):
    """Parse a timezone-aware timestamp, or return None when missing or invalid."""
    if not isinstance(value, str):
        return None
    try:
        return timestamp(value)
    except ValueError:
        return None


def _hours(later, earlier):
    return (later - earlier).total_seconds() / 3600


def _row(usecase, entity, provider, fail=(), unknown=(), status=None, note=None, sources=()):
    if status is None:
        status = "FAIL" if fail else "UNKNOWN" if unknown else "PASS"
    reasons = list(fail) + list(unknown) or [note or "all derived conditions satisfied"]
    return {"usecase_id": usecase, "entity_id": entity, "provider": provider, "status": status,
            "reasons": reasons, "sources": sorted({s for s in sources if s})}


def leaver_access(data, params, now, uc="UC-01"):
    """Terminated workers lose identity-provider and cloud-native access within the SLA."""
    sla = params["sla_hours"]
    accounts = {}
    for account in data["idp_accounts"]["accounts"]:
        if account.get("worker_id"):
            accounts.setdefault(account["worker_id"], []).append(account)
    credentials = data["cloud_credentials"]["credentials"]
    rows = []
    for worker in sorted(data["hr_workers"]["workers"], key=lambda w: w["worker_id"]):
        if worker.get("status") != "terminated":
            continue
        wid = worker["worker_id"]
        sources = [data["hr_workers"].get("source")]
        term = _time(worker.get("termination_effective_at"))
        if term is None:
            rows.append(_row(uc, wid, "idp", unknown=["termination time missing or invalid in the HR export"], sources=sources))
            continue
        if term > now:
            rows.append(_row(uc, wid, "idp", status="NOT_APPLICABLE",
                             note="termination is effective after the as-of time", sources=sources))
            continue
        fail, unknown = [], []
        owned = [c for c in credentials if c.get("owner_worker_id") == wid]
        for cred in owned:
            sources.append(cred.get("source"))
            if cred.get("status") == "active":
                message = f"{cred['provider']} {cred['type']} {cred['credential_id']} still active"
                used = _time(cred.get("last_used_at"))
                if used and used > term:
                    message += f", last used {cred['last_used_at']} after termination"
                fail.append(message)
            elif cred.get("status") not in ("inactive", "disabled", "deleted"):
                unknown.append(f"{cred['provider']} credential {cred.get('credential_id')} has no recognizable status")
        matched = accounts.get(wid, [])
        if not matched and not owned:
            unknown.append("no identity-provider account or cloud credential correlated to this worker; "
                           "confirm the worker never had access")
        for account in matched:
            sources.append(data["idp_accounts"].get("source"))
            enabled = account.get("enabled")
            if type(enabled) is not bool:
                unknown.append(f"{account['account_id']}: enabled state not collected")
            elif enabled:
                days = (now - term).total_seconds() / 86400
                fail.append(f"{account['account_id']}: identity-provider account still enabled {days:.1f} days after termination")
            else:
                disabled = _time(account.get("disabled_at"))
                if disabled is None:
                    unknown.append(f"{account['account_id']}: disabled, but the disable time was not recorded")
                elif _hours(disabled, term) > sla:
                    fail.append(f"{account['account_id']}: disabled {_hours(disabled, term):.1f} h after termination; SLA {sla} h")
        rows.append(_row(uc, wid, "idp", fail, unknown, sources=sources))
    return rows


def _exclusion_valid(exclusion, now):
    try:
        return (exclusion["status"] == "approved" and bool(exclusion["approver"].strip())
                and exclusion["approver"] != exclusion["owner"]
                and bool(exclusion["compensating_control"].strip())
                and timestamp(exclusion["approved_at"]) <= now < timestamp(exclusion["expires_at"]))
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def privileged_mfa(data, params, now, uc="UC-02"):
    """Privileged accounts are covered by an enforcing MFA policy and hold a strong method."""
    groups = params["privileged_groups"]
    weak = set(params["weak_methods"])
    exclusions = {e["account_id"]: e for e in data["mfa_exclusions"]["exclusions"]}
    rows = []
    for account in sorted(data["idp_accounts"]["accounts"], key=lambda a: a["account_id"]):
        held = sorted(set(account.get("groups", [])) & set(groups))
        if not held or account.get("enabled") is not True:
            continue
        providers = sorted({groups[g] for g in held})
        provider = providers[0] if len(providers) == 1 else "multi"
        aid = account["account_id"]
        sources = [data["idp_accounts"].get("source")]
        if account.get("break_glass") is True:
            exclusion = exclusions.get(aid)
            if _exclusion_valid(exclusion, now):
                rows.append(_row(uc, aid, provider, status="NOT_APPLICABLE",
                                 note=f"break-glass account under approved exclusion {exclusion['id']}; "
                                      "tested by the break-glass procedure, not this predicate",
                                 sources=sources + [data["mfa_exclusions"].get("source")]))
            else:
                rows.append(_row(uc, aid, provider, ["break-glass account is excluded from MFA without a valid, "
                                                     "independently approved exclusion"], sources=sources))
            continue
        mfa = account.get("mfa")
        if (not isinstance(mfa, dict) or type(mfa.get("policy_enforced")) is not bool
                or not isinstance(mfa.get("methods"), list)):
            rows.append(_row(uc, aid, provider, unknown=["MFA policy assignment or registered methods not collected"],
                             sources=sources))
            continue
        fail = []
        if not mfa["policy_enforced"]:
            fail.append("no MFA-enforcing access policy applies to this privileged account")
        if not mfa["methods"]:
            fail.append("no MFA method registered")
        elif not [m for m in mfa["methods"] if m not in weak]:
            fail.append("only weak methods registered: " + ", ".join(mfa["methods"]))
        rows.append(_row(uc, aid, provider, fail, sources=sources))
    return rows


def change_approval(data, params, now, uc="UC-03"):
    """Each production deployment traces to an independently approved change at the deployed commit."""
    pulls = {p["merge_commit_sha"]: p for p in data["pull_requests"]["pull_requests"]
             if p.get("merged") is True and p.get("merge_commit_sha")}
    emergencies = {e["deployment_id"]: e for e in data["emergency_changes"]["changes"]}
    window = params["emergency_review_hours"]
    rows = []
    for deploy in sorted(data["deployments"]["deployments"], key=lambda d: d["deployment_id"]):
        did, provider = deploy["deployment_id"], deploy.get("provider", "unknown")
        sources = [data["deployments"].get("source")]
        if deploy.get("environment") != "prod":
            rows.append(_row(uc, did, provider, status="NOT_APPLICABLE",
                             note="non-production deployment; outside the production change population", sources=sources))
            continue
        sha = deploy.get("commit_sha")
        if not isinstance(sha, str) or not sha.strip():
            rows.append(_row(uc, did, provider, unknown=["deployment record lacks a commit SHA; the deployed artifact "
                                                         "cannot be traced to an approved change"], sources=sources))
            continue
        pull = pulls.get(sha)
        if pull is None:
            emergency = emergencies.get(did)
            if emergency is None:
                rows.append(_row(uc, did, provider, [f"deployed commit {sha} has no merged pull request and no "
                                                     "emergency change record"], sources=sources))
                continue
            sources.append(data["emergency_changes"].get("source"))
            fail, unknown = [], []
            approved, deployed = _time(emergency.get("approved_at")), _time(deploy.get("deployed_at"))
            if approved is None or deployed is None:
                unknown.append("emergency approval time or deployment time missing")
            else:
                if emergency.get("approver") in (None, "", deploy.get("deployer")):
                    fail.append("emergency change not approved by someone other than the deployer")
                if _hours(approved, deployed) > window:
                    fail.append(f"retrospective approval {_hours(approved, deployed):.1f} h after deployment; limit {window} h")
            rows.append(_row(uc, did, provider, fail, unknown, sources=sources,
                             note=f"emergency change {emergency['change_id']} approved retrospectively within {window} h"))
            continue
        sources.append(data["pull_requests"].get("source"))
        if not pull.get("head_sha"):
            rows.append(_row(uc, did, provider, unknown=[f"PR {pull['number']} head commit not collected"], sources=sources))
            continue
        approvals = [r for r in pull.get("reviews", []) if r.get("state") == "APPROVED"]
        independent = [r for r in approvals if r.get("reviewer") != pull.get("author")]
        current = [r for r in independent if r.get("commit_id") == pull["head_sha"]]
        fail = []
        if not approvals:
            fail.append(f"PR {pull['number']} merged without an approval")
        elif not independent:
            fail.append(f"PR {pull['number']} approved only by its author")
        elif not current:
            fail.append(f"PR {pull['number']} approval predates the final commit {pull['head_sha']}; "
                        "the deployed code was not reviewed")
        rows.append(_row(uc, did, provider, fail, sources=sources,
                         note=f"PR {pull['number']} independently approved at the merged head commit"))
    return rows


def _aws_trails(config, scope, fail, unknown, params):
    trails = config.get("trails")
    if not isinstance(trails, list):
        unknown.append("CloudTrail trail configuration not collected")
    elif not any(t.get("IsMultiRegionTrail") is True and t.get("IsLogging") is True for t in trails):
        fail.append("no multi-region CloudTrail trail is actively logging")


def _azure_activity(config, scope, fail, unknown, params):
    settings = config.get("subscription_diagnostic_settings")
    if not isinstance(settings, list):
        unknown.append("subscription diagnostic settings not collected")
        return
    def exports_admin(setting):
        destination = setting.get("workspaceId") or setting.get("eventHubAuthorizationRuleId") or setting.get("storageAccountId")
        logs = setting.get("logs") or []
        return bool(destination) and any(l.get("category") == "Administrative" and l.get("enabled") is True for l in logs)
    if not any(exports_admin(s) for s in settings):
        fail.append("no diagnostic setting exports the Administrative activity log category")


def _gcp_audit(config, scope, fail, unknown, params):
    sinks = config.get("sinks")
    if not isinstance(sinks, list):
        unknown.append("log sinks not collected")
    elif not any(s.get("destination") and "cloudaudit.googleapis.com" in (s.get("filter") or "cloudaudit.googleapis.com")
                 for s in sinks):
        fail.append("no log sink routes Cloud Audit Logs to the monitored destination")
    if scope.get("hosts_ephi") is True:
        audit = config.get("auditConfigs")
        if not isinstance(audit, list):
            unknown.append("IAM policy auditConfigs not collected")
            return
        for service in params["gcp_ephi_services"]:
            types = {c.get("logType") for a in audit if a.get("service") in (service, "allServices")
                     for c in a.get("auditLogConfigs", [])}
            if not {"DATA_READ", "DATA_WRITE"} <= types:
                fail.append(f"Data Access audit logs (DATA_READ and DATA_WRITE) not enabled for {service} in an ePHI project")


def audit_logging(data, params, now, uc="UC-04"):
    """Each cloud scope exports audit logs, and a canary event reaches the monitored destination within the SLO."""
    checks = {"aws": _aws_trails, "azure": _azure_activity, "gcp": _gcp_audit}
    slo = params["canary_slo_minutes"]
    rows = []
    for scope in sorted(data["log_scopes"]["scopes"], key=lambda s: s["scope_id"]):
        fail, unknown = [], []
        provider = scope.get("provider")
        if provider not in checks:
            unknown.append("unsupported provider")
        else:
            checks[provider](scope.get("config") or {}, scope, fail, unknown, params)
        canary = scope.get("canary")
        emitted = _time(canary.get("emitted_at")) if isinstance(canary, dict) else None
        if emitted is None:
            unknown.append("no canary event emitted for this scope in the test window")
        elif canary.get("received_at") is None:
            fail.append(f"canary {canary.get('event_id')} not received by the monitored log destination")
        else:
            received = _time(canary["received_at"])
            latency = None if received is None else (received - emitted).total_seconds() / 60
            if latency is None or latency < 0:
                unknown.append("canary receipt time invalid")
            elif latency > slo:
                fail.append(f"canary arrived after {latency:.0f} min; SLO {slo} min")
        rows.append(_row(uc, scope["scope_id"], provider, fail, unknown, sources=[data["log_scopes"].get("source")]))
    return rows


def ephi_encryption(data, params, now, uc="UC-05"):
    """Datastores tagged as holding ePHI use an enabled customer-managed key with bounded rotation."""
    keys = {k["key_id"]: k for k in data["keys"]["keys"]}
    rows = []
    for store in sorted(data["datastores"]["datastores"], key=lambda d: d["datastore_id"]):
        sid, provider = store["datastore_id"], store.get("provider")
        sources = [data["datastores"].get("source")]
        tags = store.get("data_tags")
        if not isinstance(tags, list):
            rows.append(_row(uc, sid, provider, unknown=["reviewed data classification tags missing"], sources=sources))
            continue
        if params["data_tag"] not in tags:
            rows.append(_row(uc, sid, provider, status="NOT_APPLICABLE",
                             note="no ePHI tag in the reviewed classification", sources=sources))
            continue
        fail, unknown = [], []
        encryption = store.get("encryption")
        if not isinstance(encryption, dict) or type(encryption.get("enabled")) is not bool:
            unknown.append("encryption configuration not collected")
        elif not encryption["enabled"]:
            fail.append("encryption at rest disabled")
        elif encryption.get("key_source") == "provider_managed":
            fail.append("encrypted with a provider-managed key; Acme policy requires a customer-managed key for ePHI")
        elif encryption.get("key_source") != "customer_managed":
            unknown.append("key source not recognized")
        else:
            key = keys.get(encryption.get("key_id"))
            sources.append(data["keys"].get("source"))
            if key is None:
                unknown.append(f"key {encryption.get('key_id')} metadata not collected")
            else:
                if key.get("state") != "enabled":
                    fail.append(f"key {key['key_id']} state is {key.get('state')}")
                period = key.get("rotation_period_days")
                if period is None:
                    unknown.append(f"automatic rotation configuration for {key['key_id']} not collected")
                elif type(period) is not int or period <= 0:
                    unknown.append(f"rotation period for {key['key_id']} is not a positive whole number of days")
                elif period > params["max_rotation_days"]:
                    fail.append(f"key {key['key_id']} rotates every {period} days; limit {params['max_rotation_days']} days")
        rows.append(_row(uc, sid, provider, fail, unknown, sources=sources))
    return rows


def backup_restore(data, params, now, uc="UC-06"):
    """Tier 1 datastores are backed up within the RPO and recently restored with integrity verified."""
    backups = {b["datastore_id"]: b for b in data["backups"]["protected_resources"]}
    exercises = {}
    for exercise in data["restore_tests"]["exercises"]:
        exercises.setdefault(exercise["datastore_id"], []).append(exercise)
    rows = []
    for store in sorted(data["datastores"]["datastores"], key=lambda d: d["datastore_id"]):
        sid, provider = store["datastore_id"], store.get("provider")
        sources = [data["datastores"].get("source"), data["backups"].get("source"), data["restore_tests"].get("source")]
        if store.get("criticality") != "tier1":
            rows.append(_row(uc, sid, provider, status="NOT_APPLICABLE",
                             note="not tier 1; recovery objectives are set by a separate standard", sources=sources[:1]))
            continue
        fail, unknown = [], []
        backup = backups.get(sid)
        if backup is None:
            fail.append("not assigned to any backup plan in the backup service export")
        else:
            point = _time(backup.get("last_recovery_point_at"))
            if point is None:
                unknown.append("latest recovery point time missing from the backup export")
            elif _hours(now, point) > params["rpo_hours"]:
                fail.append(f"latest recovery point is {_hours(now, point):.1f} h old; RPO {params['rpo_hours']} h")
        history = [e for e in exercises.get(sid, []) if _time(e.get("performed_at"))]
        if not history:
            fail.append("no restore exercise recorded in the authoritative restore register")
        else:
            latest = max(history, key=lambda e: _time(e["performed_at"]))
            age = (now - _time(latest["performed_at"])).total_seconds() / 86400
            if age > params["restore_max_age_days"]:
                fail.append(f"latest restore exercise is {age:.0f} days old; limit {params['restore_max_age_days']} days")
            if latest.get("integrity_verified") is not True:
                fail.append(f"restore {latest['exercise_id']} lacked integrity verification")
            elapsed = latest.get("elapsed_hours")
            if type(elapsed) not in (int, float):
                unknown.append(f"restore {latest['exercise_id']} elapsed time not recorded")
            elif elapsed > params["rto_hours"]:
                fail.append(f"restore {latest['exercise_id']} took {elapsed} h; RTO {params['rto_hours']} h")
        rows.append(_row(uc, sid, provider, fail, unknown, sources=sources))
    return rows


def vulnerability_sla(data, params, now, uc="UC-07"):
    """Scanned compute assets have no open vulnerability older than its severity SLA."""
    findings = {}
    for finding in data["vulnerabilities"]["findings"]:
        findings.setdefault(finding["asset_id"], []).append(finding)
    sla = params["sla_days"]
    rows = []
    for asset in sorted(data["compute_assets"]["assets"], key=lambda a: a["asset_id"]):
        aid, provider = asset["asset_id"], asset.get("provider")
        fail, unknown = [], []
        scanned = _time(asset.get("last_scanned_at"))
        if scanned is None or (now - scanned).total_seconds() / 86400 > params["scan_max_age_days"]:
            unknown.append(f"no successful scan within {params['scan_max_age_days']} days; open findings may be incomplete")
        for finding in sorted(findings.get(aid, []), key=lambda f: f["finding_id"]):
            if finding.get("status") != "open" or finding.get("severity") not in sla:
                continue
            first = _time(finding.get("first_seen_at"))
            if first is None:
                unknown.append(f"{finding['finding_id']}: first-seen time missing")
                continue
            age = (now - first).total_seconds() / 86400
            if age > sla[finding["severity"]]:
                fail.append(f"{finding['finding_id']} {finding['severity']} open {age:.0f} days; SLA {sla[finding['severity']]} days")
        rows.append(_row(uc, aid, provider, fail, unknown,
                         sources=[data["compute_assets"].get("source"), data["vulnerabilities"].get("source")]))
    return rows


def access_review(data, params, now, uc="UC-08"):
    """Privileged access reviews cover the full group, are decided independently and revocations take effect."""
    membership = {}
    for account in data["idp_accounts"]["accounts"]:
        for group in account.get("groups", []):
            membership.setdefault(group, set()).add(account["account_id"])
    snapshots = {s["campaign_id"]: s for s in data["review_snapshots"]["snapshots"]}
    rows = []
    for campaign in sorted(data["access_reviews"]["campaigns"], key=lambda c: c["campaign_id"]):
        cid, group = campaign["campaign_id"], campaign["group"]
        fail, unknown = [], []
        items = campaign.get("items", [])
        snapshot = snapshots.get(cid)
        if snapshot is None:
            unknown.append("no group-membership snapshot at campaign start; the review population cannot be reconciled")
        else:
            missing = sorted(set(snapshot["members"]) - {i["account_id"] for i in items})
            if missing:
                fail.append("review population incomplete; not reviewed: " + ", ".join(missing))
        for item in items:
            account = item["account_id"]
            if item.get("decision") not in ("keep", "revoke"):
                fail.append(f"{account}: no reviewer decision recorded")
            if item.get("reviewer") == account:
                fail.append(f"{account}: reviewed by the account holder")
            if item.get("decision") == "revoke" and account in membership.get(group, set()):
                fail.append(f"{account}: revocation decided {item.get('decided_at')} but {group} membership is still present")
        completed, due = _time(campaign.get("completed_at")), _time(campaign.get("due_at"))
        if completed is None:
            (fail if due and due < now else unknown).append("campaign not completed")
        elif due and completed > due:
            fail.append(f"completed {(completed - due).days} days after the due date")
        rows.append(_row(uc, cid, campaign.get("provider"), fail, unknown,
                         sources=[data["access_reviews"].get("source"), data["idp_accounts"].get("source")]))
    return rows


REGISTRY = {
    "leaver_access": leaver_access,
    "privileged_mfa": privileged_mfa,
    "change_approval": change_approval,
    "audit_logging": audit_logging,
    "ephi_encryption": ephi_encryption,
    "backup_restore": backup_restore,
    "vulnerability_sla": vulnerability_sla,
    "access_review": access_review,
}


def counts(rows):
    tally = Counter(r["status"] for r in rows)
    return {s: tally[s] for s in STATES}


def run(specs, data, now):
    """Run every use case in the specification against the loaded source records."""
    rows = []
    for spec in specs["usecases"]:
        rows += REGISTRY[spec["implementation"]](data, spec["parameters"], now, spec["id"])
    by_usecase = {spec["id"]: counts([r for r in rows if r["usecase_id"] == spec["id"]]) for spec in specs["usecases"]}
    return rows, by_usecase
