{% for item in summary %}
 * **`{{ item.alertname }}`**: {{ item.num_firings }} total (*{{ item.total_time }}*)
{% else %}
No alerts.
{% endfor %}
