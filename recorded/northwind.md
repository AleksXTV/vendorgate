# Vendor review: Northwind Insights GmbH

**Recommendation: APPROVE WITH CONDITIONS** · risk High · model said `approve_with_conditions` at 43% · **human sign-off required**

> Approve with conditions because while the vendor meets several key requirements, there are violations regarding subprocessors, liability caps, and auto-renewal terms, alongside several contradictions between sales claims and contractual documentation

## Guardrails applied
- Model confidence 43% is below the 70% auto-decision threshold.

## Pipeline
- **Intake: Guard every document, mask personal data** (pipeline, injection, pii): 8 personal-data values masked before analysis; no prompt injection found.
- **Inspect the vendor's install script (never executed)** (script): Verdict: benign (benign administration, severity none); 0 lines flagged.
- **Extract key contract terms verbatim** (extract): 11 of 11 terms found with source positions.
- **Rerank the policy library: which requirements apply?** (rerank): 8 of 12 requirements apply: P7-endpoint-agents, P3-breach-notification, P10-ai-training, P5-liability, P1-eu-personal-data, P4-subprocessors, P11-security-attestation, P6-auto-renewal.
- **Compare what the vendor told us across documents** (compare): 4 statements contradicted elsewhere in the packet (10 conflicting passage pairs).
- **Verify each sales promise against the binding documents** (grounding): 5 sales claims checked: 4 contradicted by the documents, 0 not backed by them.
- **Decide each applicable requirement: meets, violates, not established** (decide): 5 met, 3 violated, 0 not established.
- **Decide the recommendation, then apply hard guardrails** (decide): Model: approve_with_conditions (43%); final after guardrails: approve_with_conditions; risk High. Human sign-off required.
- **Fill the board memo and vendor email, then Verify the memo** (fill, grounding): Memo drafted; self-check: 98% grounded, 0 line(s) flagged for a human to check.

## Policy requirements
| Requirement | Result | Confidence |
|---|---|---|
| P1-eu-personal-data EU personal data: residency and transfers | meets | 93% |
| P3-breach-notification Breach notification | meets | 97% |
| P4-subprocessors Subprocessors | violates | 99% |
| P5-liability Liability cap for data processors | violates | 99% |
| P6-auto-renewal Auto-renewal and termination | violates | 98% |
| P7-endpoint-agents Software installed on our infrastructure | meets | 67% |
| P10-ai-training AI vendors: no training on our data | meets | 99% |
| P11-security-attestation Independent security attestation | meets | 71% |

## Conflicts between vendor documents
- sales_email: "The subscription is month-to-month, so you can cancel any time." vs contract: "The initial subscription term is twelve (12) months from the Effective Date."
- sales_email: "The subscription is month-to-month, so you can cancel any time." vs contract: "The subscription renews automatically for successive twelve (12) month terms unless either party gives written notice of non-renewal at least ninety (90) days before the end of the then-current term."
- sales_email: "We do not use any subprocessors; everything runs on our own infrastructure." vs contract: "Backups and support tooling may be processed by Provider's subprocessors in the United States as listed in Schedule 2."
- sales_email: "We do not use any subprocessors; everything runs on our own infrastructure." vs contract: "Provider may engage subprocessors and will notify Customer of new subprocessors by updating Schedule 2 fourteen (14) days in advance."
- sales_email: "We do not use any subprocessors; everything runs on our own infrastructure." vs contract: "Schedule 2 currently lists: Amazon Web Services EMEA SARL (backups, United States), Zendesk Inc. (support ticketing, United States)."
- sales_email: "If anything ever goes wrong, we notify customers of a security incident within 24 hours." vs contract: "Provider will notify Customer of a Security Incident affecting Customer Data without undue delay and in any event within seventy-two (72) hours of becoming aware of it."
- sales_email: "All of your customer data stays in our Frankfurt data center and never leaves the EU." vs questionnaire: "Primary storage is in Frankfurt (AWS eu-central-1)."
- sales_email: "All of your customer data stays in our Frankfurt data center and never leaves the EU." vs questionnaire: "Encrypted backups are replicated to AWS us-east-1."
- sales_email: "We do not use any subprocessors; everything runs on our own infrastructure." vs questionnaire: "Yes: Amazon Web Services (hosting and backups) and Zendesk (support tickets)."
- sales_email: "If anything ever goes wrong, we notify customers of a security incident within 24 hours." vs questionnaire: "Within 72 hours of confirmation."

## Sales claims vs. binding documents
- [contradicted] All of your customer data stays in our Frankfurt data center and never leaves the EU.
- [contradicted] We do not use any subprocessors; everything runs on our own infrastructure.
- [contradicted] If anything ever goes wrong, we notify customers of a security incident within 24 hours.
- [supported] Our SOC 2 Type II report was issued in March 2026 and we are happy to share it under NDA.
- [contradicted] The subscription is month-to-month, so you can cancel any time.

## Findings behind the decision (generated, then checked by Verify)
The vendor provides customer analytics SaaS with an annual value of approximately USD 84000.
The contract specifies an initial term of twelve months with a ninety-day renewal notice.
The contract lists Amazon Web Services EMEA SARL and Zendesk Inc. as subprocessors.
Encrypted backups are replicated to AWS us-east-1

## What to ask the vendor
1. Update contract to list all subprocessors and their locations
2. Align contract with sales claim regarding month-to-month cancellation
3. Align contract with sales claim regarding 24-hour breach notification
4. Clarify data residency and backup locations to ensure EU compliance
5. Negotiate liability cap to meet P5 requirements
6. Resolve auto-renewal terms to meet P6 requirements
7. Reconcile subprocessor usage claims with actual infrastructure usage

## Draft email to the vendor

The procurement review for Northwind Insights GmbH has resulted in a conditional approval. While several requirements are met, we have identified critical discrepancies between sales communications and the contract. Specifically, we require clarification regarding the month-to-month cancellation claim versus the twelve-month initial term and auto-renewal clause. Additionally, the contract must align with sales claims regarding subprocessor usage, the 24-hour breach notification window, and the assurance that data remains exclusively within the EU, as current documentation indicates US-based backups and subprocessors. Please provide updated documentation or formal confirmation addressing these contradictions to proceed with the final approval process

_12 Clocked requests · 115 credits · 4.7 s_