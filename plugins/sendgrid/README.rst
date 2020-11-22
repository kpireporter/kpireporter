==================
kpireport-sendgrid
==================

.. image:: https://img.shields.io/pypi/v/kpireport-sendgrid
   :target: https://pypi.org/project/kpireport-sendgrid

.. code-block::

   pip install kpireport-sendgrid

Send the report as an email using `SendGrid <https://sendgrid.com/>`_. This
plugin utilizes SendGrid's API, and you must generate an API key that has
the "Mail Send" permission to authenticate and send the report.

Images or other attachments are by default embedded within the email, but you
can optionally link them in as remote assets instead. Remote linking requires
that the report additionally be placed somewhere accessible over the Internet,
via, e.g., the :ref:`static-plugin`, :ref:`s3-plugin`, or :ref:`scp-plugin`
plugins.
