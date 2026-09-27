# Reusable analytical templates

Select the few templates that support the task. Use compact tables in chat or structured artifacts for complex work; do not require the user to fill these in. Empty or unknown cells are preferable to invented values.

## Intelligence brief

Decision / owner / audience:
Question and alternatives:
Geography / population / as-of date / horizon:
Success criteria and constraints:
Key judgments with confidence and evidence:
Strongest countercase:
Recommendation and tradeoffs:
Immediate action, owner, and timing:
Reversal or review trigger:
Material gaps:

## Collection plan

| Question | Decision impact | Evidence required | Best source | Independent check | Freshness | Gap / next step |
|---|---|---|---|---|---|---|

## Claim ledger

| ID | Proposition | Status | Source and locator | Evidence family | Period | Supports / contradicts | Confidence and reason | Decision implication |
|---|---|---|---|---|---|---|---|---|

## Assumptions register

| Assumption | Why needed | Evidence status | What if false? | Test | Trigger to revise |
|---|---|---|---|---|---|

## Issue tree work plan

| Parent question | Subquestion | Hypothesis | Metric or observation | Test | Priority | Finding |
|---|---|---|---|---|---|---|

## Competing hypotheses

| Evidence (with source) | H1 | H2 | H3, if plausible | Diagnostic value | Dependence or caveat |
|---|---|---|---|---|---|

Use support / contradiction / neutral / unknown with a short reason. Do not turn the table into a vote count or automatic probability.

## Stakeholders

| Stakeholder / group | Formal role | Evidence of authority | Interests / constraints | Impact on them | Position and uncertainty | Dependencies | Engagement |
|---|---|---|---|---|---|---|---|

## Risk register

| Risk mechanism | Trigger | Exposure | Likelihood basis | Impact range | Existing control evidence | Residual risk | Owner / action | Warning indicator |
|---|---|---|---|---|---|---|---|---|

## Scenario comparison

| Scenario | Conditions and mechanism | Implications | Leading signs | Option performance | Contingent action |
|---|---|---|---|---|---|

## Forecast log

| Date | Resolvable proposition | Deadline | Resolution source and rule | Probability / range | Basis | Evidence | Update trigger | Outcome |
|---|---|---|---|---|---|---|---|---|

## Experiment

Hypothesis / target participant / intervention or offer / observed behavior / baseline / success and failure thresholds / time and cost / bias controls / next decision.

## Adversarial review

| Claim or recommendation | Strongest objection | Supporting counterevidence | Decision severity | Correction or test | Residual uncertainty |
|---|---|---|---|---|---|

## Structured record for optional validation

Use JSON shaped as below. `sources` and `claims` require unique IDs. Cite source IDs in each claim's `evidence`; source `family` records dependence. `premises` links inference or recommendation to other claim IDs. Include limitations rather than filling gaps with plausible numbers. This example illustrates format and contains no factual evidence.

```json
{
  "question": "Which action should we choose?",
  "as_of": "2026-09-27",
  "sources": [
    {"id":"E1","title":"Example supplied source","locator":"S21, PDF p. 2","family":"example-origin"}
  ],
  "claims": [
    {"id":"C1","text":"Example attributed proposition","kind":"attributed_claim","evidence":[{"source_id":"E1","locator":"PDF p. 2"}],"premises":[],"confidence":"low","confidence_reason":"Illustrative record only; factual support must be inspected."},
    {"id":"C2","text":"Example action conditional on C1","kind":"recommendation","evidence":[],"premises":["C1"],"rationale":"This is a format example, not an actual recommendation."}
  ],
  "forecasts": [],
  "limitations": ["Example only; not a validated analysis."]
}
```

Optional forecast fields: `id`, `question`, `deadline` (YYYY-MM-DD), `resolution_rule`, `probability` (0-1), `basis`, and `outcome` (0 or 1 only when resolved). For unresolved questions omit `outcome`. A structural pass never certifies substantive truth.

Run `python3 <intel-skill-directory>/scripts/check_evidence.py <record.json>` and inspect both errors and warnings. Do not report an evidence audit completed on this check alone.
