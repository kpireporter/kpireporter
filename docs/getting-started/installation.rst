.. _getting-started-installation:

=============
Installation
=============

KPI Reporter is a Python module that is installable via ``pip``:

.. image:: https://img.shields.io/pypi/v/kpireport
   :target: https://pypi.org/project/kpireport

.. image:: https://img.shields.io/pypi/pyversions/kpireport
   :target: https://pypi.org/project/kpireport

.. code-block:: shell

  pip install kpireport

Docker
======

A `Docker image
<https://hub.docker.com/repository/docker/kpireporter/kpireporter>`_ is available
on DockerHub with all dependencies required by :ref:`all available plugins
<plugins-available>`.

.. image:: https://images.microbadger.com/badges/version/kpireporter/kpireporter.svg
   :target: https://hub.docker.com/repository/docker/kpireporter/kpireporter

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

Plugins
=======

If you are not using the distributed Docker image, and are installing KPI
Reporter via pip, you will have to install some small set of additional plugins
to get started. Two simple plugins you may want are the :ref:`plot-plugin` and
:ref:`static-plugin` ones.

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
