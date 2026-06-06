# ADR-003: Data quality as a scored, rule-based contract

- **Status:** Accepted
- **Date:** 2026-05-19
- **Context layer:** governance

## Context

"Is this data good?" is unanswerable until it is *measurable*. Without a quality
contract, bad data propagates silently to gold tables and dashboards, and trust is
lost in one incident but rebuilt over months. We need quality expressed as
enforceable rules with a single comparable score per dataset, decoupled from any one
storage engine.

## Decision

Express quality as **six pluggable rule classes** — freshness, validity,
completeness, uniqueness, consistency — each subclassing a common `base_rule`
interface, producing a per-dataset **scorecard**. Rules are config-driven
(`config/dq_rules.json`), the scorer aggregates to a single comparable number, and
the `validate` path is importable/testable independent of the API and UI.

## Alternatives considered

| Option | Why rejected |
|---|---|
| Great Expectations / Soda off the shelf | Right answer in production, but adopting a framework before understanding the rule taxonomy hides the design judgment this POC exists to demonstrate. The `base_rule` interface is GE-compatible in spirit. |
| Ad-hoc SQL assertions per table | No common score, no reuse, no taxonomy — every team reinvents freshness checks slightly differently. |
| Hard pass/fail gates only | Binary gates can't express "92% complete, degrading" — you need a score to trend and to set SLA thresholds against. |

## Consequences

- **Positive:** New rules drop in behind one interface; every dataset gets a
  comparable score that can trend and alert. Validation logic is unit-tested in
  isolation from transport.
- **Negative / cost:** Scoring weights are a judgment call — a misweighted scorecard
  can mask a critical dimension behind good aggregate health.
- **Risk accepted:** Rules run on data at rest (batch), so detection lags ingestion.
  Acceptable until freshness SLOs demand inline checks.

## What changes at 100×

At platform scale this becomes an **observability surface**, not a batch report:
freshness/volume/distribution monitors emit metrics continuously, scorecards back
data SLOs with alerting, and the single score fans out into per-dimension SLAs owned
by data-product teams. The rule engine stays; the delivery shifts from "run and
print" to "monitor and page."
