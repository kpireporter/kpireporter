.. _prometheus-plugin:
.. currentmodule:: kpireport.plugins.prometheus

===========
Prometheus
===========

The Prometheus plugin provides both a Datasource capable of returning PromQL
query results and a View that summarizes alerts fired by the Prometheus server
over the report interval.

Example
=======

.. image:: ../../examples/rendered/html/prometheus.alert_summary.png
   :target: /examples/latest-ops-report/index.html
   :alt: prometheus.alert_summary

Configuration
-------------

.. literalinclude:: ../../examples/prometheus.yaml
   :language: yaml

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

.. autoclass:: PrometheusAlertSummary
   :members:
   :show-inheritance: