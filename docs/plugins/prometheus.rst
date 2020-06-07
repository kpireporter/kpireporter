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

.. image:: ../../examples/rendered/html/prometheus.alert_summary.png
   :target: ../../examples/latest-ops-report/index.html
   :alt: prometheus.alert_summary

.. autoclass:: PrometheusAlertSummary
   :members:
   :show-inheritance:
