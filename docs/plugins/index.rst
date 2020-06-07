.. _plugin-index:

========
Plugins
========

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

.. _plugins-available:

Available plugins
=================

.. toctree::
   :maxdepth: 1
   :glob:

   *

KPI Reporter only comes with a the :ref:`plot-plugin` and :ref:`static-plugin`
plugins by default. For additional functionality, you should install the
plugins relevant for your report.

Installing plugins
==================

Plugins are Python modules, and can be installed however you prefer, e.g.,
with ``pip``. Plugins must be installed into the same Python path as
KPI Reporter, as that is how they are automatically discovered at runtime.

Plugins provided as part of KPI reporter are prefixed ``kpireport-``, and so
are installed like the following:

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


Developing plugins
==================

Please refer to the :ref:`plugin development guide <development-plugins>`.
