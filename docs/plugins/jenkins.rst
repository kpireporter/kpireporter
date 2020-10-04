.. _jenkins-plugin:

========
Jenkins
========

.. image:: https://img.shields.io/pypi/v/kpireport-jenkins
   :target: https://pypi.org/project/kpireport-jenkins

.. code-block::

   pip install kpireport-jenkins

The Jenkins plugin provides both a Datasource for querying the Jenkins API, as
well as a View for displaying a summary of job/build statuses. The list of
jobs can be filtered to target jobs that are of interest in your reporting.

.. raw:: html

   <details>
     <summary><strong>Show/hide example configuration YAML</strong></summary>

.. literalinclude:: ../../examples/jenkins.yaml
   :language: yaml

.. raw:: html

   </details>

Datasource
==========

.. currentmodule:: kpireport_jenkins.datasource
.. autoclass:: JenkinsDatasource
   :members:
   :show-inheritance:
   :exclude-members: init

Build summary
=============

.. figure:: ../../examples/rendered/html/jenkins.build_summary.png
   :target: ./examples/latest-ci-report/index.html
   :alt: jenkins.build_summary

   An example showing jobs matching a certain name pattern "\*-app"

.. currentmodule:: kpireport_jenkins.build_summary
.. autoclass:: JenkinsBuildSummary
   :members:
   :show-inheritance:

.. autoclass:: JenkinsBuildFilter
   :members:
