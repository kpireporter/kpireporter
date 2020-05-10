from functools import lru_cache
import jenkins
import pandas as pd
import re

from kpireport.datasource import Datasource
from kpireport.view import View


class JenkinsDatasource(Datasource):
    def init(self, host=None, user=None, api_token=None):
        if not host:
            raise ValueError("Missing required paramter: 'host'")
        if not host.startswith("http"):
            host = f"http://{host}"

        self.client = jenkins.Jenkins(host, username=user, password=api_token)

    def query(self, fn_name, *args, **kwargs):
        fn = getattr(self, fn_name, None)
        if not (fn and callable(fn)):
            raise ValueError(f"No such method {fn_name} for Jenkins client")

        return fn(*args, **kwargs)

    def get_all_jobs(self):
        jobs = pd.DataFrame.from_records(self.client.get_all_jobs())
        # Filter by jobs that don't have child jobs
        leaf_jobs = jobs[jobs.jobs.isna()]
        return leaf_jobs

    def get_job_info(self, job_name):
        job_info = self.client.get_job_info(job_name, depth=1)
        df = pd.json_normalize(job_info, "builds")
        # Transpose the health report information into our result table--
        # this is a bit of a hack but it avoids having to make two calls
        # to our datasource (DataFrames don't handle mixed dict/list data)
        return df.assign(**job_info["healthReport"])


class JenkinsBuildFilter:
    name_filter = None

    def __init__(self, name=None, invert=False):
        self.invert = invert
        if name:
            self.name_filter = self._process_filters(name)

    def _process_filters(self, filters):
        if not (isinstance(filters, list) or isinstance(filters, str)):
            raise ValueError((
                "Invalid filter type, only string or "
                "list of strings supported"))
        if not isinstance(filters, list):
            filters = [filters]
        return [re.compile(f) for f in filters]

    def filter_job(self, job):
        allow = True

        if self.name_filter:
            job_name = job["fullname"]
            allow &= all(f.search(job_name) for f in self.name_filter)

        if self.invert:
            allow = not allow

        return allow


class JenkinsBuildSummary(View):
    def init(self, datasource="jenkins", filters={}):
        self.datasource = datasource
        self.filters = JenkinsBuildFilter(**filters)

    @lru_cache
    def template_vars(self):
        jobs = self.datasources.query(self.datasource, "get_all_jobs")

        summary = []
        for _, row in jobs.iterrows():
            if not self.filters.filter_job(row):
                continue
            job_name = row["fullname"]
            job_url = row["url"]
            builds = self.datasources.query(
                self.datasource, "get_job_info", job_name)
            score = builds["score"].iloc[0]
            # Reverse order of builds, Jenkins returns most recent ones first
            build_list = builds.iloc[::-1].T.to_dict().values()
            summary.append(dict(
                name=job_name,
                url=job_url,
                score=score,
                builds=build_list,
            ))

        return dict(summary=summary)

    def render_html(self, j2):
        template = j2.get_template("plugins/jenkins_build_summary.html")
        return template.render(**self.template_vars())

    def render_md(self, j2):
        template = j2.get_template("plugins/jenkins_build_summary.md")
        return template.render(**self.template_vars())
