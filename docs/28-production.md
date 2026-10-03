# Move from the portfolio lab to a production program

**Objective:** identify the concrete engineering and governance work needed before this reference implementation can support a real service.

## What must change

The offline engine accepts supplied facts. Production requires authenticated collectors, trustworthy scope, comprehensive provider semantics, secure storage, historical operation, tested deployment and organizational ownership. Adding cloud credentials to the demo is not enough.

| Area | Current artifact | Production work |
|---|---|---|
| Population | Nine declared synthetic workloads | Hierarchy discovery, pagination, reconciliation, lifecycle history |
| Source data | Synthetic observation fixture | Authenticated APIs, request provenance and source reliability review |
| Adapters | One narrow prevention field per provider | Full service contracts, effective-policy interpretation and integration tests |
| Process controls | Supplied normalized booleans | HR/IdP/ITSM/CI/backup joins with reproducible derivation |
| Evidence integrity | Local SHA-256 manifest | Signed manifests, trusted identity/time, protected retention and recovery |
| Storage | Local files | Encrypted regional stores with access logging and lifecycle policy |
| Scheduling | Manual CLI/CI | Monitored schedules/events, queues, retries and dead-letter workflow |
| Exceptions | JSON records | Authenticated approval workflow and expiry enforcement |
| Framework mapping | Thematic candidate guidance | Requirement-level licensed mapping and assessor review |
| Availability | Local run | Operational SLOs, on-call ownership, recovery and capacity testing |

## Pilot sequence

Choose one service and one cloud. Confirm scope, owners and obligations. Implement inventory and two or three high-value controls end to end. Compare automated results with a manual expert review. Investigate disagreements before expanding the catalog.

Run the collector in shadow mode, where it produces findings without automatically changing production. Measure false positives, missing coverage, freshness, operational cost and owner response. Introduce preventive gates only after testing applicability and rollback. Keep broad automatic remediation out of the first rollout.

## Collector engineering requirements

Implement bounded retries, timeouts, continuation-token handling, rate limits, request correlation, idempotency and scope-level run status. Validate account/project identity and expected owner. Distinguish absent configuration from permission denial or unsupported resource type. Record source and adapter versions.

Use contract fixtures captured from authorized sandboxes and sanitized for tests. Validate unknown provider fields conservatively. Add schema-version migration plans so an API change cannot silently flip a control result. Test partial collection, duplicate events, reordered events and delayed consistency.

## Secure delivery

Protect the repository and release process. Separate deployment, collection, remediation, evidence administration and report approval roles. Use a secrets manager where credentials cannot be replaced with federation. Scan dependencies and artifacts, pin reviewed versions, log administration and test recovery of the assurance system itself.

The included cloud templates are pilot building blocks. Validate syntax with native tools, review plans/what-if/change sets, deploy only to an approved sandbox and capture actual tests. They have not been applied to live accounts in this project.

## Migration and scale

Import existing evidence with clear provenance and original timestamps. Do not relabel imported documents as newly performed controls. Reconcile legacy exception records and stale owners. Define retention for old schemas and rule versions.

Scale by partitioning collection along provider, account/project and region boundaries. Keep control definitions centralized where appropriate, but preserve regional evidence custody. Load-test query and storage volumes using synthetic data. Measure backlog and API throttling under expected peak conditions.

## Go-live gates

Required gates include approved scope, proven source coverage, validated test semantics, secure identities, tested storage/recovery, known operating costs, documented exceptions, reviewer acceptance, incident ownership and an approved rollback plan. The GRC manager and authorized service owners decide readiness with the evidence in hand.

## Public publication

The project lives in its own standalone repository at `/home/ssmith/repos/ita-grc-continuous-assurance`. Set GitHub Pages to GitHub Actions and use the provided manual Pages workflow after choosing the repository. The build uses relative links and publishes only the generated site. The repository's regular check workflow tests code and validates the site.

Build from the repository root with `python3 scripts/build_site.py`. The generated `site/` directory is the publication artifact. A portfolio site can link to the eventual GitHub Pages URL. No cloud resources need to be deployed to publish the synthetic demonstration. [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Review the generated source package and synthetic report before public deployment. Public publication and live cloud deployment are separate actions from local build and validation.
