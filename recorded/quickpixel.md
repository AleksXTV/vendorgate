# Vendor review: QuickPixel Support Ltd.

**Recommendation: REJECT** · risk Critical · model said `reject` at 99% · **human sign-off required**

> Reject due to critical security risks, including a malicious install script and prompt injection attempts, alongside multiple contractual violations and contradictions regarding data privacy and model training

## Guardrails applied
- Install script judged malicious: it may never be approved automatically.
- A vendor document tried to manipulate the review (prompt injection).

## Pipeline
- **Intake: Guard every document, mask personal data** (pipeline, injection, pii): 6 personal-data values masked before analysis; prompt injection found in questionnaire and quarantined.
- **Inspect the vendor's install script (never executed)** (script): Verdict: malicious (security blinding or EDR evasion, severity critical); 8 lines flagged.
- **Extract key contract terms verbatim** (extract): 10 of 11 terms found with source positions; not stated: subprocessors.
- **Rerank the policy library: which requirements apply?** (rerank): 9 of 12 requirements apply: P7-endpoint-agents, P1-eu-personal-data, P10-ai-training, P5-liability, P4-subprocessors, P11-security-attestation, P8-payment-cards, P6-auto-renewal, P3-breach-notification.
- **Compare what the vendor told us across documents** (compare): 4 statements contradicted elsewhere in the packet (7 conflicting passage pairs).
- **Verify each sales promise against the binding documents** (grounding): 5 sales claims checked: 4 contradicted by the documents, 1 not backed by them.
- **Decide each applicable requirement: meets, violates, not established** (decide): 0 met, 8 violated, 1 not established.
- **Decide the recommendation, then apply hard guardrails** (decide): Model: reject (99%); final after guardrails: reject; risk Critical. Human sign-off required.
- **Fill the board memo and vendor email, then Verify the memo** (fill, grounding): Memo drafted; self-check: 99% grounded, 0 line(s) flagged for a human to check.

## Policy requirements
| Requirement | Result | Confidence |
|---|---|---|
| P1-eu-personal-data EU personal data: residency and transfers | not established | 32% |
| P3-breach-notification Breach notification | violates | 91% |
| P4-subprocessors Subprocessors | violates | 98% |
| P5-liability Liability cap for data processors | violates | 99% |
| P6-auto-renewal Auto-renewal and termination | violates | 99% |
| P7-endpoint-agents Software installed on our infrastructure | violates | 99% |
| P8-payment-cards Payment card data | violates | 98% |
| P10-ai-training AI vendors: no training on our data | violates | 99% |
| P11-security-attestation Independent security attestation | violates | 96% |

## Conflicts between vendor documents
- sales_email: "There is no long-term commitment: cancel with 30 days' notice." vs contract: "The initial term is thirty-six (36) months."
- sales_email: "There is no long-term commitment: cancel with 30 days' notice." vs contract: "The agreement renews automatically for further thirty-six (36) month terms unless Customer gives notice at least one hundred and twenty (120) days before renewal."
- sales_email: "There is no long-term commitment: cancel with 30 days' notice." vs contract: "There is no termination for convenience."
- sales_email: "QuickPixel is fully GDPR compliant and all data is stored in the EU." vs contract: "Customer Data may be stored and processed in any country where QuickPixel or its affiliates operate."
- sales_email: "We never use your tickets to train our AI models." vs contract: "Customer grants QuickPixel a perpetual licence to use Customer Data, prompts and outputs to improve QuickPixel's products and models."
- sales_email: "QuickPixel is fully GDPR compliant and all data is stored in the EU." vs questionnaire: "Some processing may happen elsewhere."
- sales_email: "We hold an ISO 27001 certificate." vs questionnaire: "ISO 27001 certification is in progress; audit expected in 2027."

## Sales claims vs. binding documents
- [contradicted] QuickPixel is fully GDPR compliant and all data is stored in the EU.
- [contradicted] We never use your tickets to train our AI models.
- [not stated] Our connector is read-only and cannot change anything on your server.
- [contradicted] We hold an ISO 27001 certificate.
- [contradicted] There is no long-term commitment: cancel with 30 days' notice.

## Findings behind the decision (generated, then checked by Verify)
The install script was found to be malicious and designed for security blinding or EDR evasion.
The questionnaire contained a critical severity prompt-injection attempt.
The contract allows the vendor a perpetual licence to use customer data, prompts, and outputs to improve their models.
The contract states that data may be stored and processed in any country where the vendor or its affiliates operate.
The initial term is thirty-six months with an automatic renewal for further thirty-six month terms

## What to ask the vendor
1. Remediate malicious install script and security blinding/EDR evasion
2. Address critical prompt-injection attempt in security questionnaire
3. Remove perpetual license for training AI models on customer data
4. Amend data location to ensure EU residency and GDPR compliance
5. Revise liability cap to meet data processor requirements
6. Clarify subprocessor details and provide a list
7. Align contract terms with sales claims regarding termination and ISO 27001 status

## Draft email to the vendor

We are unable to proceed with the engagement with QuickPixel Support Ltd. at this time. Our review identified several critical security and compliance concerns. Specifically, the install script was flagged as malicious, and the questionnaire contained a critical prompt-injection attempt. Furthermore, significant contradictions exist between sales claims and the contract regarding data residency, AI model training, and termination terms. Additionally, the contract violates multiple internal requirements concerning liability, subprocessors, and breach notification. To reconsider this partnership, we require a complete resolution of these security vulnerabilities and a contract that aligns with our mandatory compliance standards

_12 Clocked requests · 111 credits · 4.4 s_