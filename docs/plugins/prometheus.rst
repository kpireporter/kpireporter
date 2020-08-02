.. _prometheus-plugin:
.. currentmodule:: kpireport_prometheus

===========
Prometheus
===========

The Prometheus plugin provides both a Datasource capable of returning PromQL
query results and a View that summarizes alerts fired by the Prometheus server
over the report interval.

.. raw:: html

   <details>
     <summary><strong>Show/hide example configuration YAML</strong></summary>

.. literalinclude:: ../../examples/prometheus.yaml
   :language: yaml

.. raw:: html

   </details>

Datasource
==========

.. autoclass:: PrometheusDatasource
   :members:
   :show-inheritance:
   :exclude-members: init

Views
=====

Alert summary
-------------

.. figure:: ../../examples/rendered/html/prometheus.alert_summary.png
   :target: ../../examples/latest-ops-report/index.html
   :alt: prometheus.alert_summary

   An example rendered alert summary. The timeline at the top displays the
   points in time when any alert was firing over the report window.
   Individual alert labels are not shown; the view's purpose is to highlight
   trends or patterns that can be looked at in more detail at the source.

.. autoclass:: PrometheusAlertSummary
   :members:
   :show-inheritance:
