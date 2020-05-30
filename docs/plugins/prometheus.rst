.. currentmodule:: kpireport.plugins.prometheus

===========
Prometheus
===========

The Prometheus plugin provides a Datasource and a View that summarizes alerts
fired by the Prometheus server over the report interval.

Example
=======

Configuration
-------------

.. literalinclude:: ../../examples/prometheus.yaml
   :language: yaml

Datasource
==========

.. autoclass:: PrometheusDatasource
   :members:
   :show-inheritance:

Views
=====

Alert summary
-------------

.. autoclass:: PrometheusAlertSummary
   :members:
   :show-inheritance: