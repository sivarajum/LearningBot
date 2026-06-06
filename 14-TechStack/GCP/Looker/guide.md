# Looker Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. Core Concepts
- Models, Explores, Views; LookML as semantic layer
- Users/roles; folders/content
- PDTs (persistent derived tables); connections to DBs

### 2. First Steps
- Connect to warehouse (BigQuery, etc.)
- Create a View and Explore; build a Look and a Dashboard

### 3. LookML Basics
```lookml
view: orders {
  sql_table_name: analytics.orders ;;
  dimension: order_id { primary_key: yes; type: number; sql: ${TABLE}.order_id ;; }
  measure: total_revenue { type: sum; sql: ${TABLE}.revenue ;; }
}
```

## Level 2 – Production Patterns

### Modeling
- Consistent naming; primary keys; foreign keys for joins
- Derived tables for complex transforms; materialize heavy PDTs
- Access filters; row-level security via user attributes

### Performance
- Push-down to warehouse; avoid N+1 joins; set limits
- Cache policy tuning; PDT persistence; schedule rebuilds
- Use aggregate awareness where applicable

### Governance
- Git-integrated dev; code review; content validation
- Folders/permissions per team; content access controls
- Versioning and deploy processes

## Level 3 – Architect Playbook

### Reliability
- Validate explores; lint LookML; tests for fields/explores
- DR: repo backups; promote via branches/environments

### Security & Compliance
- Row/column security; user attributes; data privacy
- SSO/SAML/OIDC; audit logs; monitor runaway queries

### Operations
- Content lifecycle: stale content pruning
- SLA on dashboards; monitor query performance and concurrency

## Ops Cheat Sheet

| Task | Path/Tool | Note |
| --- | --- | --- |
| Dev mode | Toggle in UI | safe edits |
| Deploy | Git + prod deploy | code flow |
| Lint | Content Validator | quality |
| Schedule | Dash schedules | delivery |

## Architecture Patterns

```mermaid
flowchart LR
  Warehouse[DW (e.g., BigQuery)] --> LookML[LookML Models/Views]
  LookML --> Explores[Explores]
  Explores --> Dash[Looks/Dashboards]
  Dash --> Users[Users/Stakeholders]
  LookML --> Git[Git Versioning]
```

## Checklist Before Production
- [ ] LookML validated; explores tested; PK/FK correct
- [ ] Row/column security enforced; SSO configured; audit logs on
- [ ] PDT/aggregates tuned; cache policies set; schedules defined
- [ ] Git workflow + code review; content access reviewed
- [ ] Monitoring on query performance and schedule failures

