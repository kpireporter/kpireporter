{% for job in summary %}
{% for build in job.builds -%}
  {%- if build.result == "SUCCESS" -%}
:small_blue_diamond:
  {%- else -%}
:small_red_triangle_down:
  {%- endif -%}
{%- endfor -%}

{%- if job.score >= 80 -%}
:sunny:
{%- elif job.score >= 60 -%}
:sun_behind_cloud:
{%- elif job.score >= 40 -%}
:cloud:
{%- elif job.score >= 20 -%}
:rain_cloud:
{%- elif job.score >= 0 -%}
:thunder_cloud_and_rain:
{%- endif %} <{{ job.url }}|{{ job.name }}>
{% else %}
No jobs found. :shrug:
{% endfor %}