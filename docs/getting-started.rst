================
Getting started
================

Installation
============

KPI Reporter is a Python module that is installable via ``pip``:

.. image:: https://img.shields.io/pypi/pyversions/kpireport
   :target: https://pypi.org/project/kpireport

.. code-block:: shell

  pip install kpireport

Docker
------

A Docker image is available on DockerHub with all dependencies required by
:ref:`all available plugins <plugins-available>`:

.. image:: https://images.microbadger.com/badges/version/diurnalist/kpireporter.svg
   :target: https://hub.docker.com/repository/docker/diurnalist/kpireporter

Usage
=====

Invoking the installed bin script without any arguments will default to
generating a report over a window ending at the current date and starting at
one week ago. To specify different windows, use the ``--start-date`` and
``--end-date`` options.

.. code-block:: shell

  # Generate report over last 7 days
  kpireport --config-file kpireport.yaml

  # Generate report from last week
  kpireport --config-file kpireport.yaml \
    --start-date $(date +%Y-%m-%d -d'-2 week') \
    --end-date $(date +%Y-%m-%d -d'-1 week')

Configuration file
==================

A report is declared entirely within a YAML file consisting of a few main
sections: ``datasources``, ``views``, and ``outputs``. In each section, you
can declare as many plugin instances as you wish (to e.g., declare multiple
database :ref:`Datasources <api-datasource>` or multiple :ref:`Plot
<plot-plugin>` visualizations in your report). As dictated by the `YAML spec
<https://yaml.org/spec/1.2/spec.html#id2759669>`_, duplicate keys (IDs) are
not allowed; ensure that each plugin instance has its own ID unique to its
section.

.. note::

  It is possible to specify multiple configuration files when generating a
  report. In this case, the configurations are merged together, with the last
  file taking priority:

  .. code-block:: shell

      kpireport -c base-config.yaml -c extra-config.yaml

Schema
------

.. code-block:: yaml

  ---
  title: (str) The title of the report

  datasources:
    (str) datasource ID:
      plugin: (str) The name of the plugin
      args: (dict) Plugin arguments (plugin-specific)

  views:
    (str) view ID:
      plugin: (str) The name of the plugin
      title: (str, optional) A title to display above the rendered view
      cols: (int, optional) The column span of the view in the report layout
      args: (dict) Plugin arguments (plugin-specific)

  outputs:
    (str) output ID:
      plugin: (str) The name of the plugin
      args: (dict) Plugin arguments (plugin-specific)


Plugins
=======

KPI Reporter features an extensible and composable plugin architecture that
allows you to customize the tool to suit your specific needs. There are three
types of plugins:

**Datasource plugins**
  allow you to interface with specific backend databases and services. A
  Datasource abstracts the backend behind a simple query interface and handles
  transforming data into a standard :class:`pandas.DataFrame` object
  containing the results for interoperability with various Views.
  :ref:`Read more about Datasources <api-datasource>`.
**View plugins**
  allow you to implement visualizations of data, but can also be used to
  render static information. Typically Views will fetch data from Datasources
  and then somehow transform or summarize the data visually. Views are
  expected to output text, but can generate binary "blobs" that can later
  be linked to or rendered inline. :ref:`Read more about Views <api-view>`.
**Output driver plugins**
  allow you to change how a report is published, e.g., written to a local
  disk, uploaded to a cloud storage system, or directly sent as mail.
  :ref:`Read more about Output drivers <api-output-driver>`.

Plugins are Python modules, and can be installed however you prefer, e.g.,
with ``pip``. Plugins must be installed into the same Python path as
KPI Reporter, as that is how they are automatically discovered at runtime.

KPI Reporter only comes with a the :ref:`plot-plugin` and :ref:`static-plugin`
plugins by default. For additional functionality, you should install the
plugins relevant for your report.

Plugins provided as part of KPI Reporter project are prefixed ``kpireport-``,
and so are installed like the following:

.. code-block:: shell

    # Install KPI reporter with MySQL, Prometheus and SendGrid plugins
    pip install \
      kpireport \
      kpireport-mysql \
      kpireport-prometheus \
      kpireport-sendgrid

.. note::

    It is possible to install all available plugins via the ``all`` extra:

      .. code-block:: shell

          pip install kpireport[all]


Examples
========

Top-of-funnel report
--------------------

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
---------

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
----------

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
