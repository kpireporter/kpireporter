=============
kpireport-scp
=============

.. image:: https://img.shields.io/pypi/v/kpireport-scp
   :target: https://pypi.org/project/kpireport-scp

.. code-block::

   pip install kpireport-scp

The ``scp`` plugin writes the report contents to local disk and then copies
them to a remote host via ``scp``. This can be used to copy the report to a
server's webroot or simply keep a backup around.

.. note::

   Currently only the HTML format is supported.
