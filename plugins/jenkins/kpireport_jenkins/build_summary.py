from functools import lru_cache
import re

from kpireport.view import View


class JenkinsBuildFilter:
    """Filters a list of Jenkins jobs/builds by a general criteria

    Currently only filtering by name is supported, but this class can be
    extended in the future to filter on other attributes, such as build status
    or health.

    :type name: Union[str, List[str]]
    :param name: the list of name filter patterns. These will be compiled
                    as regular expressions. In the case of a single filter,
                    a string can be provided instead of a list.
    :type invert: bool
    :param invert: whether to invert the filter result
    """

    name_filter = None

    def __init__(self, name=None, invert=False):
        self.invert = invert
        if name:
            self.name_filter = self._process_filters(name)

    def _process_filters(self, filters):
        if not (isinstance(filters, list) or isinstance(filters, str)):
            raise ValueError(
                ("Invalid filter type, only string or " "list of strings supported")
            )
        if not isinstance(filters, list):
            filters = [filters]
        return [re.compile(f) for f in filters]

    def filter_job(self, job):
        """Checks a job against the current filters

        :type job: dict
        :param job: the Jenkins job
        :rtype: bool
        :returns: whether the job passes the filters
        """
        allow = True

        if self.name_filter:
            job_name = job["fullname"]
            allow &= all(f.search(job_name) for f in self.name_filter)

        if self.invert:
            allow = not allow

        return allow


class JenkinsBuildSummary(View):
    """Display a list of jobs with their latest build statuses, and health.

    :formats: html, md

    :type datasource: str
    :param datasource: the Datasource ID to query for Jenkins data
    :type filters: dict
    :param filters: optional filters to limit which jobs are rendered in
                    the view. These filters are directly passed to
                    :class:`JenkinsBuildFilter`.
    """

    def init(self, datasource="jenkins", filters={}):
        self.datasource = datasource
        self.filters = JenkinsBuildFilter(**filters)

    @lru_cache(maxsize=1)
    def _template_vars(self):
        jobs = self.datasources.query(self.datasource, "get_all_jobs")

        summary = []
        for _, row in jobs.iterrows():
            if not self.filters.filter_job(row):
                continue
            job_name = row["fullname"]
            job_url = row["url"]
            builds = self.datasources.query(self.datasource, "get_job_info", job_name)
            score = builds["score"].iloc[0]
            # Reverse order of builds, Jenkins returns most recent ones first
            build_list = builds.iloc[::-1].T.to_dict().values()
            summary.append(
                dict(
                    name=job_name,
                    url=job_url,
                    score=score,
                    builds=build_list,
                )
            )

        return dict(summary=summary)

    def _render(self, j2, fmt):
        template = j2.get_template(f"jenkins_build_summary.{fmt}")
        return template.render(**self._template_vars())

    def render_html(self, j2):
        return self._render(j2, "html")

    def render_md(self, j2):
        return self._render(j2, "md")

    def render_slack(self, j2):
        return self._render(j2, "slack")
