.. _configuration-file:

===================
Configuration file
===================

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

A full example
==============

For more examples see :ref:`getting-started-examples`.

.. literalinclude:: ../../examples/full.yaml
   :language: yaml

Schema
======

.. jsonschema:: ../../schema/configuration.schema.json
   :lift_definitions:
   :auto_reference:

View instances
==============

The View instances defined in the ``views`` section define what is rendered in
the final report. Each view is placed into a layout in the order in which they
are defined, i.e., the first declared View will show at the top, and the last
will show at the bottom.

The report layout follows a simple grid system with 6 columns. By default, Views
will each take the full width. However, you can change this with the ``cols``
configuration option. For example, consider this configuration:

.. code-block:: yaml

  views:
    view_a:
    view_b:
      cols: 2
    view_c:
      cols: 4
    view_d:
    view_e:
      cols: 3
    view_f:
      cols: 3

The views would be rendered in the report like this:

  +------------------------------+
  | View A                       |
  +---------+--------------------+
  | View B  | View C             |
  +---------+--------------------+
  | View D                       |
  +---------------+--------------+
  | View E        | View F       |
  +---------------+--------------+
