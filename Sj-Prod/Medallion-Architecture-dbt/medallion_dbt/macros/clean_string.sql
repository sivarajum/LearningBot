/*
  clean_string.sql
  ----------------
  dbt macro: standardise a text column.

  Usage in a model:
      {{ clean_string('column_name') }}

  What it does:
    1. TRIM  — remove leading/trailing whitespace
    2. LOWER — normalise to lowercase
    3. REGEXP_REPLACE — collapse multiple internal spaces to a single space

  Example:
    Input  : '  John   DOE  '
    Output : 'john doe'
*/

{% macro clean_string(column_name) %}
    TRIM(
        REGEXP_REPLACE(
            LOWER(TRIM({{ column_name }})),
            '\\s+',
            ' '
        )
    )
{% endmacro %}
