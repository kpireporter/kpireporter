==================
kpireport-jenkins
==================

.. image:: https://img.shields.io/pypi/v/kpireport-jenkins
   :target: https://pypi.org/project/kpireport-jenkins

.. code-block::

   pip install kpireport-jenkins

The Jenkins plugin provides both a Datasource for querying the Jenkins API, as
well as a View for displaying a summary of job/build statuses. The list of
jobs can be filtered to target jobs that are of interest in your reporting.

Datasource
==========

.. raw:: html

   <details>
     <summary><strong>Show/hide example configuration YAML</strong></summary>

.. literalinclude:: ../_extra/examples/ci_report.yaml
   :language: yaml

.. raw:: html

   </details>

Build summary
=============

.. figure:: ../_extra/examples/rendered/html/jenkins.build_summary.png
   :target: ./examples/latest-ci-report/index.html
   :alt: jenkins.build_summary

   An example showing jobs matching a certain name pattern "\*-app"
