.. _jenkins-plugin:

========
Jenkins
========

.. include:: ../../plugins/jenkins/README.rst

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

Changelog
=========

.. release-notes::
   :relnotessubdir: plugins/jenkins/releasenotes
