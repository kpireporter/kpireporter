# {{ report.title }}

{{ report.start_date | datetimeformat }} to {{ report.end_date | datetimeformat }}

{% for view in views %}
  {% include "view.md" %}
{% endfor %}
