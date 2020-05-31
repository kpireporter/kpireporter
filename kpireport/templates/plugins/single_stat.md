**{{ label }}** {% if stat_delta is not none -%}
  ({{ direction }} {{ stat_delta }})
{%- endif %}