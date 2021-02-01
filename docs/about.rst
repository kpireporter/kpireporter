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

You can `purchase a one-year license <https://kpireporter.com/pricing/>`_ for $99/year
(for individuals/small businesses) or $499/year (for larger businesses.) You can use
discretion about which tier you belong to.

.. _about-comparisons:

Comparisons
===========

There are several existing products and applications that do some of what KPI
Reporter does. Many of them do a far better job depending on your specific
use-case. Here is a brief summary of the ones I know of.

Cloud SaaS
----------

All of these services are rather sophisticated and focus on delivering user-friendly
interfaces so that a wider range of employees can be useful. They are also more
expensive for that reason. Most support some overlapping (and typically wider) set of
data sources and reporting/visualization capabilities as KPI Reporter.

* `Chartio <https://chartio.com/>`_: subscriptions start at $40/month per user after a
  14 day trial.
* `Databox <https://databox.com>`_: subscriptions start at $49/month for 10 users and
  10 data sources.
* `Daily Metrics <https://thedailymetrics.com/>`_: a subscription is $10/month
* `Grafana Enterprise Reporting
  <https://grafana.com/docs/grafana/latest/enterprise/reporting/>`_: pricing is only
  available on request, putting it safely above any of the other products.
* `Grow.com <https://grow.com>`_: pricing available on request, similar to Grafana
  Enterprise.
* `Klipfolio <https://www.klipfolio.com/>`_: a subscription is $70/month after a 14-day
  trial.
* `Sunrise KPI <https://sunrisekpi.com/>`_: a subscription is $15/month after a 14-day
  trial.

On-premises
-----------

* `Zoho Analytics <https://www.zoho.com/analytics/onpremise.html>`_: while principally
  another cloud SaaS product, Zoho Analytics is the only offering I could find that
  supports an on-premises deployment at time of writing. The on-premises version is
  $30/month per seat, with a minimum of 5 seats, so $150/month. The online version is
  $45/month for the same number of users.
