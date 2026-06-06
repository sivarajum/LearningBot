# dbt Guide – Basic → Architect

## Level 1 – Launch & Basics

### 1. **Quick Setup**
```bash
pip install dbt-core dbt-postgres

# Initialize project
dbt init my_project
```

### 2. **First Model**
```sql
-- models/my_first_model.sql
SELECT 
    id,
    name,
    created_at
FROM {{ source('raw', 'users') }}
WHERE status = 'active'
```

### 3. **Run Models**
```bash
# Run all models
dbt run

# Run specific model
dbt run --select my_first_model

# Test
dbt test
```

## Level 2 – Production Patterns

### Incremental Models
```sql
{{
    config(
        materialized='incremental',
        unique_key='id'
    )
}}

SELECT * FROM {{ source('raw', 'events') }}

{% if is_incremental() %}
    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

### Macros
```sql
-- macros/date_spine.sql
{% macro date_spine(start_date, end_date) %}
    SELECT date_day
    FROM (
        SELECT 
            DATEADD(day, seq4(), '{{ start_date }}') as date_day
        FROM TABLE(GENERATOR(ROWCOUNT => 10000))
    )
    WHERE date_day <= '{{ end_date }}'
{% endmacro %}
```

## Level 3 – Architect Playbook

### dbt Cloud
```yaml
# dbt_project.yml
name: my_project
version: 1.0.0
profile: my_profile

models:
    my_project:
        materialized: table
        +tags: ["daily"]
```

## Ops Cheat Sheet

| Task | Command | Notes |
| --- | --- | --- |
| Run | `dbt run` | Run models |
| Test | `dbt test` | Run tests |
| Docs | `dbt docs generate` | Generate docs |
| Compile | `dbt compile` | Compile SQL |

## Checklist Before Production

- [ ] Set up proper project structure
- [ ] Implement incremental models
- [ ] Set up testing
- [ ] Configure documentation
- [ ] Set up scheduling
- [ ] Implement proper error handling
- [ ] Set up monitoring
- [ ] Optimize performance

## Learning Path Links
- Tracks: `LearningTracks/Data-Engineer-GCP/track.md`, `LearningTracks/Data-Engineering/track.md`
- Projects: `Projects/GCP-DataEngineer/starter/06-dbt-incremental.md`, `Projects/Data-Engineering/starter/05-dbt-incremental.md` and `Projects/Integrated/data-engineer-gcp-capstone.md`
- Mastery: `Mastery/dbt/` (quiz, scenarios, flashcards)
