{% test accepted_range(model, column_name, min_value, max_value) %}
select
  {{ column_name }} as value
from {{ model }}
where ({{ column_name }} < {{ min_value }}) or ({{ column_name }} > {{ max_value }})
{% endtest %}

