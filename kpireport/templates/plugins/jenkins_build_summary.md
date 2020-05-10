{% for job in summary %}
 * {{ job.name }}: {{ job.score }}% healthy ([view job]({{ job.url }}))
{% else %}
No jobs found.
{% endfor %}