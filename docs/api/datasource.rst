============
Datasources
============

.. currentmodule:: reportcard.datasource

A Datasource is responsible for taking a query input string and returning its
result in the form of a :class:`pandas.DataFrame` instance. One instance
of a Datasource may be used by multiple :class:`View` instances.

Datasources are only initialized when they are expiclitly declared within the
report configuration. When the Datasource is initialized, any arguments
included in the report configuration are passed as keyword arguments to its
:meth:`Datasource.init` function (**Note**: this is *not* the same as Python's
built-in :meth:`__init__`.) Each Datasource is required to provide both
:meth:`Datasource.init`, which is responsible for setting up the Datasource
with any additional state, and :meth:`Datasource.query`, which provides the
mechanism to execute a given query and return a :class:`pandas.DataFrame` with
the results back to the caller.

To create your own Datasource, it is simplest to extend the
:class:`Datasource` class, though this is not required. It is required to
return a :class:`pandas.DataFrame` instance, as this is the API contract with
the View layer; it allows Views to use a variety of Datasources as seamlessly
as possible.

Example: a custom Datasource
============================

This Datasource will interact with a HTTP/JSON API as its backing data store.
The input query string is passed to the API as a ``query`` parameter. The JSON
result is parsed into a :class:`pandas.DataFrame` via
:meth:`pandas.DataFrame.from_records`.

.. code-block:: python

    import pandas as pd
    from reportcard.datasource import Datasource
    import requests

    class HTTPDatasource(Datasource):
        def init(self, api_host=None):
            if not api_host:
                raise ValueError("'api_host' is required")
            self.api_host = api_host

        def query(self, input):
            res = requests.get(self.api_host, params=dict(query=input))
            return pd.DataFrame.from_records(res.json())

As with all plugins, your plugin should register itself as an `entry_point`_
under the namespace ``reportcard.datasource``. We name it ``http`` in this
example. When your plugin is installed alongside the reportcard package, it
should be automatically loaded for use when the report runs.

.. code-block::

  [options:entry_points]
  reportcard.datasource =
      http = custom_module:HTTPDatasource

You can configure your Datasource in a report by declaring it in the
``datasources`` section. The ``plugin`` name must match the entry_point name
(here, ``http``.) Any arguments passed in the ``args`` key are passed to
:meth:`Datasource.init` on instantiation as keyword arguments.

.. code-block:: yaml

    datasources:
      custom_datasource:
        plugin: http
        args:
          api_host: https://api.example.com/v1/search

You can name the Datasource as you wish (here, ``custom_datasource``); Views
can invoke your Datasource via this ID.

Example: an RPC Datasource
==========================

Instead of passing the query input to another service/database, it is possible
to implement your own Datasource that provides an RPC-like interface. This can
allow you to custom-tailor your parsing and transformation of the result
returned by the backing service, as well as create more complex "queries" that
compose multiple calls to the backing service. You could even front multiple
backing services as a single Datasource interface. Here is a fully-formed
example:

.. code-block:: python

    from datetime import datetime, timedelta
    import pandas as pd
    from reportcard.datasource import Datasource
    import requests

    class RPCDatasource(Datasource):
        def init(self, users_api_host=None, activity_api_host=None):
            if not (users_api_host and activity_api_host):
                raise ValueError((
                  "Both 'users_api_host' and 'activity_api_host' "
                  "are required."))
            self.users_api_host = users_api_host
            self.activity_api_host = activity_api_host

        def query(self, input):
            """
            Treats the "input" parameter as the name of a separate function
            on the Datasource to invoke.
            """
            fn = getattr(self, input)
            if not (fn and iscallable(fn)):
                raise ValueError(f"Query '{input}' is not supported")
            return fn()

        def get_all_users(self):
            """
            Return all users, regardless of their activity status.
            """
            users = requests.get(f"{self.users_api_host}/users")
            return pd.DataFrame.from_records(users)

        def get_active_users(self):
            """
            Return only the users active within the last month.
            """
            users = requests.get(f"{self.users_api_host}/users")
            user_ids = [u["id"] for u in users.json()]
            last_active_at = requests.get(
              f"{self.activity_api_host}/last_activity",
              params=dict(
                user_ids=user_ids.join(",")
              )
            )
            one_month_ago = datetime.now() - timedelta(months=1)
            active_in_last_month = [
              a["user_id"]
              for a in last_active_at.json()
              if datetime.fromisoformat(a["last_active_at"]) > one_month_ago
            ]
            return pd.DataFrame.from_records([
              u for u in users if u["id"] in active_in_last_month])

        def total_active_users(self):
            """
            Return just the total number of active users, not a full set
            of columnar data.
            """
            return self.get_active_users().count()

From within a View, you could then invoke your Datasource like this (we have
given the Datasource the ID ``users`` here.)

.. code-block:: python

    def render_html(self, j2):
        active_users = self.datasources.query("users", "get_active_users")
        # Do something with active users

Or, using an existing plugin, like
:class:`reportcard.plugins.plot.SingleStat`, which can be configured with just
the report configuration:

.. code-block:: yaml

    views:
      active_users:
        title: Users active in last month
        plugin: single_stat
        args:
          datasource: users
          query: total_active_users


Module: :mod:`reportcard.datasource`
====================================

.. automodule:: reportcard.datasource
   :members:

.. _entry_point: https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins