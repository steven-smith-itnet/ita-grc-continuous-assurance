# Network, compute, containers and service configuration

**Objective:** constrain reachable attack paths and keep workloads in a supported, monitored configuration. Storage metadata is only one part of the service boundary.

## Build a service communication model

Start from data flows and identify client, application, database, control-plane, administrative and backup paths. Record source/destination identity, protocol, port, region, encryption, purpose and owner. Separate ingress from egress. A service with a private database may still export data through unrestricted outbound connections.

Map business paths to provider constructs. AWS uses VPCs, security groups, network ACLs, routing, endpoints, load balancers and firewall services. Azure uses VNets, NSGs, route tables, Private Link, Azure Firewall and application gateways. GCP uses VPC networks, firewall policies/rules, routes, Private Service Connect and load balancing. Their evaluation semantics differ, so translate the objective rather than copying rule names across clouds.

## Implementation sequence

1. Define approved network zones and trust boundaries, including management access and shared services.
2. Build the network through IaC with explicit rules and code review. Avoid default broad administrative ingress.
3. Restrict management access through approved identity-aware access paths and temporary authorization.
4. Create private service endpoints where justified and configure DNS for the actual client networks.
5. Restrict public endpoints independently. A private endpoint does not automatically remove every public path.
6. Configure egress controls according to data sensitivity and service dependencies.
7. Enable relevant flow, firewall, load balancer and application logs, then test that a known event arrives.
8. Validate allowed and denied paths from representative clients. Preserve route, DNS, firewall and identity context.
9. Re-run tests when routing, peering, DNS, network policies or service endpoints change.

## Compute baseline

Inventory virtual machines, images, managed runtimes, serverless functions and container clusters. For each, record supported version, patch owner, hardening standard, management identity, storage encryption, network exposure and log/agent coverage. A managed service shifts some responsibilities to the provider but leaves configuration, identities and data use with the customer.

Golden images reduce drift only when image versions are tracked and old deployments are replaced. Measure image age and deployment adoption. Distinguish package vulnerability, exploitable exposure, runtime configuration and end-of-support risk. Do not infer all four from one scanner label.

## Container and serverless additions

For Kubernetes, review API-server access, cluster and namespace RBAC, workload identities, admission policy, network policy, secret mounts, image provenance, privileged execution and node lifecycle. A cluster-wide policy may not cover every namespace or every workload type. Test a denied privileged pod in a sandbox and confirm the control cannot be bypassed by an alternate deployment identity.

For serverless, review execution role, event-source permissions, dependencies, secrets access, concurrency, outbound connectivity and dead-letter handling. The absence of a customer-managed operating system does not remove application and identity risks.

## Good, better, best

Good: documented communication matrix, reviewed IaC and periodic reachability tests. Better: baseline policies, automated exposure detection and change-triggered tests. Best: service-identity-aware segmentation, validated egress and continuous attack-path review with exceptions and owner accountability.

## Evidence and failure exercise

Create a synthetic “restricted API reachable from an unapproved segment” finding. Collect the route and policy snapshots, exact test source, expected denial, observed connection and timestamp. Determine whether the cause is a broad rule, inherited policy, peering route, DNS error or alternative endpoint. Fix through approved change, retest from both allowed and denied locations, and validate no required business path broke.

The runnable demo's `private_path_verified` is a supplied fact used to illustrate this result. No network reachability probe runs against a cloud account in the offline lab. Record that limitation when presenting it.
