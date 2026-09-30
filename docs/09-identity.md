# Identity, privileged access and lifecycle controls

**Objective:** establish who or what can access each service, why access was granted, who approved it, and whether it was removed when no longer needed.

## Start with the identity population

Join HR and contractor records to identity-provider users, application identities, cloud principals and privileged assignments. Use stable IDs and retain historical status. Include service accounts, CI workloads, managed identities, break-glass accounts, external guests, shared accounts and access granted through nested groups. A cloud-user list alone will miss federated workforce access.

Define authoritative sources for employment status, manager, role, start/end dates and third-party sponsorship. Store sensitive personnel details in the appropriate system and expose only the references required for the test.

## Joiner, mover and leaver implementation

1. HR or a sponsor creates an identity event with an effective date.
2. An approved role model translates job function into access bundles.
3. The manager and sensitive-system owner approve nonstandard access.
4. Provisioning creates or updates access through a controlled workflow.
5. The control collector compares requested access, approved access and effective grants.
6. A termination event triggers revocation of sessions, tokens, group memberships and application access according to approved targets.
7. A second query confirms removal. A closed service-desk ticket without an effective-access check is incomplete evidence.

Mover controls must remove obsolete access as well as grant new access. Emergency departures need an escalation path independent of the routine queue.

## Provider implementation

| Objective | AWS | Azure | GCP |
|---|---|---|---|
| Workforce federation | IAM Identity Center / external IdP | Microsoft Entra ID | Cloud Identity / workforce federation patterns |
| Temporary privilege | Scoped roles and session constraints | PIM eligible assignments and activation where available | Privileged Access Manager or controlled time-bound grants where supported |
| Workload access | IAM roles and STS | Managed identities / workload federation | Service accounts and Workload Identity Federation |
| Effective permissions | Identity/resource/key policies and org constraints | Azure RBAC, data-plane roles and tenant controls | IAM allow/deny policies, conditions and org constraints |
| Evidence | Role trust, assignment, CloudTrail and IdP logs | Graph, assignment history, sign-in and activity logs | IAM policies, Cloud Audit Logs and IdP records |

The table is a design map. Validate feature support, licensing and service-specific restrictions in the target environment.

## MFA and privileged access tests

Define the relevant population first: interactive privileged workforce sessions, root/break-glass use, service principals and unattended workloads are different categories. Collect conditional access or equivalent policy, assigned users, exclusions and actual sign-in behavior. Test an unauthorized session and an approved break-glass exercise. Noninteractive workloads generally need strong workload identity and credential controls rather than a human MFA prompt.

Review privilege escalation paths: who can attach policies, impersonate a service account, grant roles, change federation trust, alter a key policy or modify a production deployment pipeline? A role called “reader” can still create risk if combined with secrets access elsewhere.

## Access reviews that prove operation

Freeze the review population. Record the reviewer, decision, rationale and date for each entitlement. Escalate nonresponses. Track revocation tasks and re-query effective access after completion. Measure population completeness, reviewer completion, unresolved removals and overdue privileged reviews separately.

The demo's `access_review_at` and `access_removals_complete` facts illustrate the final normalized observations. Production must derive them from campaign decisions and verification records, not from a manually asserted boolean.

## Good, better, best

Good: reviewed access register and evidenced removals. Better: automated HR/IdP reconciliation and time-limited privileged grants. Best: governed entitlement model, event-driven revocation and continuous detection of privilege combinations, with independent review of exceptional access.

## Failure and retest exercise

Create a synthetic terminated contractor whose privileged group remains active. Confirm the test identifies effective access after the required removal time. Determine whether the root cause is missing HR events, failed provisioning, a direct grant outside the managed group or an application session that survived account disablement. Correct the actual cause, revoke residual access and retain the negative authorization test.

Relevant evidence includes HR event reference, access request, approval, effective grant, sign-in history, revocation event and verification query. The [finding template](../templates/finding.md) preserves the chain.
