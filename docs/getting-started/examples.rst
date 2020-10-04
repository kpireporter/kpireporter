.. _getting-started-examples:

=========
Examples
=========

Top-of-funnel report
====================

`View HTML <./examples/latest-top-of-funnel-report>`_

This example utilizes a MySQL Datasource and multiple Plot visualizations to
show a high-level overview of the number of new signups over the last week
(both as an running total and as a count of new signups per day).

.. raw:: html

   <details>
     <summary><strong>Show/hide configuration YAML</strong></summary>

.. literalinclude:: ../examples/mysql.yaml
   :language: yaml

.. raw:: html

   </details>

CI report
=========

`View HTML <./examples/latest-ci-report>`_

This example uses both a View and Datasource provided by the Jenkins plugin to
show an overview of build jobs and their success/failure statuses.

.. raw:: html

   <details>
     <summary><strong>Show/hide configuration YAML</strong></summary>

.. literalinclude:: ../examples/jenkins.yaml
   :language: yaml

.. raw:: html

   </details>

Ops report
==========

`View HTML <./examples/latest-ops-report>`_

This example uses both a View and Datasource provided by the Prometheus plugin
to show a visualization of some time series data representing server load, as
well as a summary of alerts fired by the Prometheus server over the report
window.

.. raw:: html

   <details>
     <summary><strong>Show/hide configuration YAML</strong></summary>

.. literalinclude:: ../examples/prometheus.yaml
    :language: yaml

.. raw:: html

   </details>
