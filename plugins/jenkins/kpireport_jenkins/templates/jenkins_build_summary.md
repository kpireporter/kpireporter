{% for job in summary %}
 * **[{{ job.name }}]({{ job.url }})** ({{ job.score }}% healthy)
{% else %}
No jobs found. :shrug:
{% endfor %}