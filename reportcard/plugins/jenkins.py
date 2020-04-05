import jenkins
import pandas as pd

from reportcard.datasource import Datasource
from reportcard.view import View


class JenkinsDatasource(Datasource):
    def init(self, host=None, user=None, api_token=None):
        if not host.startswith("http"):
            host = f"http://{host}"

        self.client = jenkins.Jenkins(host, username=user, password=api_token)

    def query(self, fn_name, *args, **kwargs):
        fn = getattr(self.client, fn_name, None)
        if not (fn and callable(fn)):
            raise ValueError(f"No such method {fn_name} for Jenkins client")

        extract_key = kwargs.pop("extract_key", None)

        res = fn(*args, **kwargs)
        
        if extract_key:
            res = res.get(extract_key)

        return pd.DataFrame.from_records(res)


class JenkinsBuildSummary(View):
    def init(self, datasource="jenkins", filter=None):
        self.datasource = datasource
        self.filter = self._process_filters(filter)

    def _process_filters(self, filters):
        name_filter = filters.get("name")
        if not name_filter:
            raise ValueError("Missing 'name' filter: only 'name' filters are supported")
        if not (isinstance(name_filter, list) or isinstance(name_filter, str)):
            raise ValueError("Invalid filter type, only string or list of strings supported")
        if not isinstance(name_filter, list):
            name_filter = [name_filter]
        return name_filter


    def render(self, env):
        jobs = self.datasources.query(self.datasource, "get_all_jobs")
        # Filter by jobs that don't have child jobs
        leaf_jobs = jobs[jobs.jobs.isna()]

        summary = []
        for job_name in leaf_jobs["fullname"]:
            # TODO: apply filters
            builds = self.datasources.query(
                self.datasource, "get_job_info", job_name,
                depth=1,
                extract_key="builds")
            build_list = builds.T.to_dict().values()
            summary.append(dict(name=job_name, builds=build_list))

        template = env.get_template("plugins/jenkins_build_summary.html")

        return template.render(summary=summary)
