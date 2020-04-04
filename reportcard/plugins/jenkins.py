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
        res = fn(*args, **kwargs)
        print(res)
        return pd.DataFrame.from_dict(res)


class JenkinsBuildSummary(View):
    def init(self, datasource="jenkins"):
        self.datasource = datasource

    def render(self, env):
        jobs = self.datasources.query(self.datasource, "get_all_jobs", folder_depth=2)
        for i, job in jobs.iterrows():
            info = self.datasources.query(self.datasource, "get_job_info", job["name"])
        return f"Found {len(jobs)} jobs."
