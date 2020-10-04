.. _getting-started-configuration:

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

Schema
======

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
