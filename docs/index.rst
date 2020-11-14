============
KPI Reporter
============

KPI Reporter is a **developer-friendly**, **highly customizable** tool for
sending periodic reports for the metrics that matter for your team or project.

Support for a variety of reporting sources is built-in, including, e.g.,
:ref:`MySQL databases <mysql-plugin>`, :ref:`Prometheus metrics
<prometheus-plugin>`, and the :ref:`Jenkins API <jenkins-plugin>`. Reports can
be sent via email (with plugins for :ref:`SMTP <smtp-plugin>` and
:ref:`SendGrid <sendgrid-plugin>`), :ref:`Slack <slack-plugin>`, or simply
rendered as :ref:`HTML <static-plugin>`.

.. note::

   **Author note**: I created this tool after being surprised that there was a
   distinct lack of simple developer-friendly reporting tools for
   communicating business and/or operational KPIs. I hope you find it useful
   as well. For more information, see :ref:`about-motivation`.

.. toctree::
   :caption: Getting started
   :maxdepth: 1

   getting-started/installation
   getting-started/configuration
   getting-started/examples
   about

.. toctree::
   :maxdepth: 1
   :caption: Plugins
   :glob:

   plugins/*

.. toctree::
   :maxdepth: 1
   :caption: Development

   development/architecture
   development/plugins
   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
