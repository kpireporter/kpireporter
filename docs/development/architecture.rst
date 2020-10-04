.. _development-architecture:

=============
Architecture
=============

Plugins
=======

KPI Reporter features an extensible and composable plugin architecture that
allows you to customize the tool to suit your specific needs. There are three
types of plugins:

**Datasource plugins**
  allow you to interface with specific backend databases and services. A
  Datasource abstracts the backend behind a simple query interface and handles
  transforming data into a standard :class:`pandas.DataFrame` object
  containing the results for interoperability with various Views.
  :ref:`Read more about Datasources <api-datasource>`.
**View plugins**
  allow you to implement visualizations of data, but can also be used to
  render static information. Typically Views will fetch data from Datasources
  and then somehow transform or summarize the data visually. Views are
  expected to output text, but can generate binary "blobs" that can later
  be linked to or rendered inline. :ref:`Read more about Views <api-view>`.
**Output driver plugins**
  allow you to change how a report is published, e.g., written to a local
  disk, uploaded to a cloud storage system, or directly sent as mail.
  :ref:`Read more about Output drivers <api-output-driver>`.

Plugins are Python modules, and can be installed however you prefer, e.g.,
with ``pip``. Plugins must be installed into the same Python path as
KPI Reporter, as that is how they are automatically discovered at runtime.
