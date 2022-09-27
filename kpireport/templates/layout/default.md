# {{ report.title }}

{{ report.start_date | datetimeformat }} to {{ report.end_date | datetimeformat }}

{% for block in blocks %}
{% include "block.md" %}
{% endfor %}
