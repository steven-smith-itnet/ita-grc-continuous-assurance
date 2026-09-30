# Optional AI assistance with human accountability

**Objective:** explore AI support for repetitive analysis while keeping evidence, test outcomes and risk decisions traceable. AI is an extension to the supplied role, not a stated requirement of the posting or a prerequisite for this project.

## Suitable tasks

Drafting a plain-language finding from structured results, suggesting candidate mappings, summarizing approved policies, identifying duplicate issue descriptions and proposing investigation questions can save analyst effort. Each output should cite the exact source fragments or structured records used and remain a draft until reviewed.

Avoid delegating control-pass decisions, legal applicability, exception approval, incident notification or independent audit conclusions to an unconstrained model. The deterministic evaluator remains the source of machine test states.

## Architecture

Use a retrieval layer over approved, access-controlled policy and control documents. Attach document ID, version, effective date and access classification to retrieved context. Separate the model's service identity from evidence-store administration and remediation permissions. Output structured suggestions with source references and an explicit uncertainty field.

Provider options include Amazon Bedrock, Azure-hosted model services and Google Vertex AI, subject to current service terms, region, data handling, retention, identity and contractual review. A local model can reduce external data transfer but still needs access controls, logging, patching and evaluation. Choosing a model is a separate implementation decision, not part of the offline demonstration.

## Prompt-injection and untrusted evidence

Treat evidence documents, tickets and retrieved text as untrusted content. An uploaded report can contain instructions to change a conclusion or reveal unrelated data. The application should restrict available tools, separate instructions from source content, enforce retrieval authorization and validate outputs against a schema. Do not allow a retrieved document to authorize actions.

Keep secrets and unnecessary personal/customer information out of model context. Prefer redacted structured facts for report drafting. Log model/version, prompt-template version, source IDs, reviewer and accepted edits according to the approved retention policy.

## Evaluation plan

Build a labeled test set with correct mappings, plausible but wrong mappings, conflicting policies, outdated sources, missing evidence and malicious embedded instructions. Measure citation accuracy, unsupported claims, retrieval access violations, refusal/uncertainty behavior and reviewer correction rate. Run regression evaluation before changing a model or prompt.

A useful acceptance criterion is that the assistant never upgrades an UNKNOWN or FAIL to PASS based on prose. Another is that each substantive finding statement links to a supplied result or explicitly marked hypothesis. Test adversarial requests to approve exceptions or execute remediation and verify those actions are unavailable.

## Agentic workflows

A bounded agent can gather approved metadata, draft a ticket and propose next steps. Use allowlisted read operations, explicit scope, maximum steps, time/cost budgets and auditable tool logs. Require an authorized human or separately controlled workflow for state-changing actions. Idempotency and rollback matter even when the model suggests the action correctly.

Start with a read-only analyst copilot. Expand only after evaluation establishes a useful, controlled benefit. “Autonomous compliance” should not be presented as an implemented capability when the system merely generates summaries.

## Good, better, best

Good: manually reviewed drafts from sanitized facts. Better: access-controlled retrieval and structured outputs with a regression suite. Best: bounded tools, continuous evaluation and documented operational accountability. The offline project implements no model calls and incurs no AI API charges.

Deliverable: [AI evaluation template](../templates/ai-evaluation.csv), ready to populate during an explicitly scoped extension.
