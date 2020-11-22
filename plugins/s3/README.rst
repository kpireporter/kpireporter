=============
kpireport-s3
=============

.. image:: https://img.shields.io/pypi/v/kpireport-s3
   :target: https://pypi.org/project/kpireport-s3

.. code-block::

   pip install kpireport-s3

The S3 plugin provides an output driver that can upload the final report
contents to an S3 bucket. Each file in the report output structure is uploaded
as a separate object. Each report is outputted with its report ID, which
contains the report interval. Additionally, a special report with the "latest"
designation is overridden with the last generated report.

.. note::

   Currently only the HTML format is supported.
