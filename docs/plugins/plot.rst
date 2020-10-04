.. _plot-plugin:
.. currentmodule:: kpireport_plot

=====
Plot
=====

Plot
====

The Plot View is a simple workhorse plugin for displaying a variety of
timeseries data. It is designed to be compatible with several Datasources and
handle most KPI graphs, which tend to plot only a single metric or perhaps
a set of related metrics.

.. raw:: html

   <details>
     <summary><strong>Show/hide example configuration YAML</strong></summary>

.. code-block:: yaml

   views:
      new_signups:
         plugin: plot
         title: New signups
         args:
            datasource: users_db
            kind: bar
            query: |
               select
                  date_format(created_at, '%%Y-%%m-%%d') as time,
                  count(*) as daily_total
               from signups
               where created_at >= {from} and created_at < {to}
               group by day(created_at)
            query_args:
               parse_dates:
                  time: '%Y-%m-%d'

.. raw:: html

   </details>

.. figure:: ../../examples/rendered/html/plot.png
   :target: ../../examples/latest-top-of-funnel-report/index.html
   :alt: plot example

   A simple line plot from MySQL data

.. autoclass:: Plot
   :members:
   :show-inheritance:

Single stat
===========

Sometimes it is useful to only show one number, and a fine-grained trend of
the number is less important; in this case, you can use a "single stat" view,
which is included as part of the Plot plugin for convenience.

.. raw:: html

   <details>
     <summary><strong>Show/hide example configuration YAML</strong></summary>

.. code-block:: yaml

   views:
      new_signups:
         plugin: single_stat
         title: New signups
         args:
            datasource: users_db
            query: |
               select count(*)
               from signups
               where created_at >= {from} and created_at < {to}
            comparison_query: |
               select count(*)
               from signups
               where created_at >= date_sub({from}, {interval})
                  and created_at < {from}
            comparison_type: percent

.. raw:: html

   </details>

.. figure:: ../../examples/rendered/html/single_stat.png
   :target: ../../examples/latest-top-of-funnel-report/index.html
   :alt: example of single stat combined with plot

   An example of a plot view combined with a single stat view

.. autoclass:: SingleStat
   :members:
   :show-inheritance:
