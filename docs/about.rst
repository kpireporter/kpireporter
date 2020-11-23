===============
About this tool
===============

.. _about-motivation:

Motivation
==========

Visualizing metrics is an incredibly common and valuable task. Virtually every
department in a business likes to leverage data when making decisions. Time and
time again I've seen developers implement one-off solutions for automatic
reporting, sometimes quick and dirty, sometimes highly polished. For example:

  * A weekly email to the entire company showing the main engagement KPIs for
    the product.
  * A weekly Slack message to a team channel showing how many alerts the on-call
    team member had to respond to in the previous week.
  * A daily summary of sales numbers and targets.

Thanks largely to Grafana, teams are customizing real-time dashboards to always
have an up-to-date view on the health of a system or the health of the business.
However, there is often value in distilling a continuum of real-time metrics
into a short digestible report. KPI Reporter attempts to make it easier to build
such reports.

A few guiding principles that shape this project:

  1. **It should be possible to run on-premises.** It is far easier to run a
     reporting tool within an infrastructure due to the amount of data sinks
     that must be accessible. Security teams should rightly raise eyebrows when
     databases are exposed externally just so a reporting tool can reach in.
  2. **It should be highly customizable.** There should not be many assumptions
     about either layout or appearance. The shape and type of data ultimately
     will drive this.
  3. **It should be possible to extend.** The space of distinct user needs is
     massive. While the tool should aim to provide a lot of useful functionality
     out of the box, it will always be the case that custom extensions will be
     required to achieve a particular implementation. The tool should embrace
     this reality.

.. _about-pricing:

Pricing
=======

KPI Reporter is **free for personal use and by noncommercial organizations**.
All commercial users are required to :ref:`obtain an annual license
<about-license>` after 30 days. I believe that if you find enough value in the
tool, this is a fair trade. You are free to implement your own third-party
plugins at any time and distribute them under any license and/or pricing you
wish.

Personal use is defined as:

  *Personal use for research, experiment, and testing for the benefit of public
  knowledge, personal study, private entertainment, hobby projects, amateur
  pursuits, or religious observance, without any anticipated commercial
  application.*

A noncommercial organization is defined as:

  *Any charitable organization, educational institution, public research
  organization, public safety or health organization, environmental protection
  organization, or government institution, regardless of the source of funding
  or obligations resulting from the funding.*

.. raw:: html

   <details>
     <summary><strong>For more details, view the project license</strong></summary>

.. literalinclude:: ../LICENSE.md
   :language: md
   :linenos:

.. raw:: html

   </details>

.. _about-license:

Obtaining a license
-------------------

There are two ways to obtain a license.

GitHub Sponsors
^^^^^^^^^^^^^^^

If you `sponsor the development of KPI Reporter
<https://github.com/sponsors/diurnalist>`_, you will get a new license each year
you are a sponsor.

One-time payment
^^^^^^^^^^^^^^^^

You can purchase a one-year license for $99/year (for individuals/small
businesses) or $499/year (for larger businesses.) You can use discretion about
which tier you belong to.

.. _about-comparisons:

Comparisons
===========

There are several existing products and applications that do some of what KPI
Reporter does. Many of them do a far better job depending on your specific
use-case. Here is a brief summary of the ones I know of.

`Daily Metrics <https://thedailymetrics.com/>`_
-----------------------------------------------

Daily Metrics is a new product that has a very similar design and offering. It
has a user-friendly web interface that allows you to hook up integrations with,
e.g., Google Analytics, MySQL, and even supports uploading custom metrics.
Additionally, the app handles sending of the mail for you, so you don't need to
manage that.

It cannot as of this writing be run on-premises, so in order to utilize
connectors like MySQL, you have to expose your database publicly on the Internet
or at minimum learn the requesting IPs of Daily Metrics in order to establish
firewall rules. Daily Metrics also only supports sending email and cannot export
your report to a file or send to Slack. However, some of these features may well
be available in the future.

The code for Daily Metrics is not published and no plugin capability exists, so
the appearance of your report will be limited by what the app supports.

A subscription is $10/month, but a free tier exists for exploring and
maintaining the simplest of reports.

`Grafana Enterprise Reporting <https://grafana.com/docs/grafana/latest/enterprise/reporting/>`_
-----------------------------------------------------------------------------------------------

Grafana has supported automatically sending a PDF of an existing dashboard for
some time now, if you are an Enterprise customer. Grafana dashboards are very
customizable, so you can express a large variety of reports. However, Grafana
only supports so many `data sources
<https://grafana.com/docs/grafana/latest/datasources/>`_. One possible downside
of Grafana Reporting is that PDFs must always be downloaded and viewed, and
cannot be simply displayed inline in email clients. The main downside for
Grafana Reporting is cost, as it requires an Enterprise plan.

Grafan Enterprise pricing is only available on request, putting it safely
above any of the other products reviewed here.

`Klipfolio <https://www.klipfolio.com/>`_
-----------------------------------------

Klipfolio is a complete analytics platform that specializes in helping you
customize rich dashboards that incorporate a variety of metrics. The product
has many `integrations <https://www.klipfolio.com/integrations>`_ to other
services, which lean heavily towards marketing products, but there are also
pure data integrations sugh as MySQL. Klipfolio cannot be run on-premises and
reports are built interactively via a web application. As with Daily Metrics,
this is perhaps a better solution for those who are not as comfortable working
with configuration files and code.

As of writing, there is no support for displaying some types of metrics that
may be valuable to development teams, such as Prometheus.

A subscription is $70/month ($49/month if annual) after a 14-day trial.

`Sunrise KPI <https://sunrisekpi.com/>`_
----------------------------------------

Sunrise KPI groups metrics from several services into one email report, and
additionally displays them in a single dashboard within a web app. Currently
the integrations are mostly with marketing software, although there is support
for calling a custom JSON API.

A subscription is $15/month ($12.50/month if annual) after a 14-day trial.
