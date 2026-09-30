# SDLC, change management and software supply chain

**Objective:** show that production changes are authorized, tested, traceable and recoverable. The control must connect a requirement or incident to the code, build and deployed artifact that changed the service.

## Define the change population

Collect production deployments from the runtime or deployment platform, then reconcile them with repository and ticket records. Starting only from approved tickets misses direct console changes and unauthorized deployments. Include infrastructure, database schema, feature flags, access policies, emergency fixes and configuration changes.

Identify the repository, branch, commit, pull request, reviewer, build run, artifact digest, test results, deployment identity, target environment and rollback reference. Use immutable identifiers where available. A mutable container tag such as `latest` is insufficient to identify the actual deployed artifact.

## Build the control path

1. Record the change purpose, risk and affected service/data boundary.
2. Require peer review and appropriate approvals before merging protected production code.
3. Run unit, integration, security and policy checks appropriate to the change.
4. Build once and promote the same identified artifact across environments.
5. Generate dependency inventory and retain security scan results with the build.
6. Use a narrowly scoped deployment identity with short-lived credentials.
7. Apply environment protection and separation of duties according to the risk decision.
8. Record deployment outcome and health checks. Stop or roll back when acceptance checks fail.
9. Reconcile observed production changes with approved pipeline runs.
10. Review emergency changes after the event within the approved procedure and retain the reason normal controls were bypassed.

## Technology choices

| Need | AWS ecosystem | Azure ecosystem | GCP ecosystem | Provider-neutral |
|---|---|---|---|---|
| Build/deploy | CodeBuild/CodePipeline or external CI | Azure DevOps/GitHub Actions | Cloud Build/Cloud Deploy | GitHub Actions, GitLab CI |
| Artifact registry | ECR and package stores | Azure Container Registry/artifacts | Artifact Registry | Approved registry with immutable identifiers |
| Policy checks | CloudFormation/IaC analysis | Bicep/ARM/Azure Policy checks | Terraform/organization policy checks | OPA/Conftest, schema and security linters |
| Identity | OIDC federation to IAM role | Federated credential/managed identity | Workload Identity Federation | No long-lived cloud keys in repository secrets where avoidable |
| Change evidence | Pipeline logs + CloudTrail | Run history + Activity Log | Build/deploy history + Audit Logs | PR, ticket and runtime artifact reconciliation |

Tool names identify implementation options. They do not establish equivalent controls without configuration and tests.

## Threats and tests

A compromised dependency can enter through a valid pull request. An unreviewed workflow change can exfiltrate credentials. A privileged user can bypass branch protections. A deployment action can use a different artifact than the one tested. Review the workflow itself as part of the software supply chain.

Pin third-party action versions to reviewed commits in a production pipeline, protect deployment environments and limit workflow permissions. For this reference project, the Pages workflow has deployment authority only when explicitly invoked, while its test workflow needs read access. Review action updates as dependencies.

Test rejected unapproved deployment, denied credential use from an untrusted branch, unsigned or unexpected artifact handling, failed security checks and successful rollback. Preserve results instead of inferring enforcement from a YAML file.

## The automated change test

The local demo evaluates `change_approved` and `change_separation_verified`. These facts are synthetic. A real adapter should derive them from reviewer identity, author identity, approval timing, bypass events and deployment records. Approval must precede deployment. A reviewer who is technically a different account but controlled by the same person may not establish genuine independence.

## Good, better, best

Good: documented change records, peer review and repeatable rollback. Better: protected pipelines, policy gates and deployment-to-approval reconciliation. Best: verified artifact provenance, tested environment separation and continuous unauthorized-change detection. Keep emergency operation possible through a controlled, observable path.

Artifacts: [CI workflow](../.github/workflows/check.yml), [Pages workflow](../.github/workflows/pages.yml), [release readiness](19-readiness.md).
