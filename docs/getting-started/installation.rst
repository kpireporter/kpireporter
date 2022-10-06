.. _getting-started-installation:

=============
Installation
=============

KPI Reporter is a Python module that is installable via ``pip``:

.. image:: https://img.shields.io/pypi/v/kpireport
   :target: https://pypi.org/project/kpireport

.. code-block:: shell

  pip install kpireport

.. _docker:

Docker
======

A `Docker image
<https://hub.docker.com/repository/docker/kpireporter/kpireporter>`_ is available
on DockerHub with all dependencies required by :ref:`all available plugins
<plugins-available>`.

.. image:: https://img.shields.io/docker/v/kpireporter/kpireporter
   :target: https://hub.docker.com/repository/docker/kpireporter/kpireporter

Usage
=====

Invoking the installed bin script without any arguments will default to
generating a report over a window ending at the current date and starting at
one week ago. To specify different windows, use the ``--start-date`` and
``--end-date`` options.

.. code-block:: shell

  # Generate report over last 7 days (default)
  kpireport --config-file my-report.yaml

  # Generate report from last week
  kpireport --config-file my-report.yaml \
    --start-date $(date +%Y-%m-%d -d'-2 week') \
    --end-date $(date +%Y-%m-%d -d'-1 week')

If you do not specify a ``--config-file`` option, the tool will attempt to find a
configuration in the following locations (in order):

1. ``./config.yaml``
2. ``/etc/kpireporter/config.yaml``

If using the :ref:`Docker image <docker>`, the configuration file can be mounted in
to one of these locations:

  .. code-block:: shell

    docker run --rm -v my-config.yaml:/etc/kpireporter/config.yaml \
      kpireporter/kpireporter:edge

Installing licenses
-------------------

.. important::
   Your license file should be kept secret! If you post your license file online or in a
   source code repository, anyone could steal your license. If you would like to request
   a new license in case of compromise, you can `send an email here
   <mailto:help@kpireporter.com>`_.

By default, KPI Reporter looks for a license files (ending in ``.pem`` or ``.key``) in
``/etc/kpireporter``. The *last file found* is used. This allows you to name your
license files by date if you want.

.. code-block:: shell

   mv path/to/license.pem /etc/kpireporter/

If using the :ref:`Docker image <docker>`, you can mount the license file inside the
container:

.. code-block:: shell

   docker run --rm -v license.pem:/etc/kpireporter/license.pem:ro \
     kpireporter/kpireporter:

You can also use the ``--license-file`` flag to load the license from a different
location.

.. code-block:: shell

   kpireport --license-file path/to/license.pem [...args]


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
      kpireport-sql \
      kpireport-prometheus \
      kpireport-sendgrid

.. note::

    It is possible to install all available plugins via the ``all`` extra:

      .. code-block:: shell

         pip install kpireport[all]

    In practice due to how pip handles (or doesn't handle) cross-dependencies this can
    be tricky. It may be better to install some "core" plugins first before attempting:

      .. code-block:: shell

         pip install kpireport kpireport-static && pip install kpireport[all]
