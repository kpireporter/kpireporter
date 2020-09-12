import jenkins
import pandas as pd

from kpireport.datasource import Datasource

import logging

LOG = logging.getLogger(__name__)


class JenkinsDatasource(Datasource):
    """Provides accessors for listing all jobs and builds from a Jenkins host.

    The Jenkins Datasource exposes an RPC-like interface to fetch all jobs,
    as well as job details for each job. The plugin will call the Jenkins API
    at the host specified using a username and API token provided as
    plugin arguments.

    Attributes:
        host (str): Jenkins host, e.g. https://jenkins.example.com.
        user (str): Jenkins user to authenticate as.
        api_token (str): Jenkins user API token to authenticate with.
    """

    def init(self, host=None, user=None, api_token=None):
        if not host:
            raise ValueError("Missing required paramter: 'host'")
        if not host.startswith("http"):
            host = f"http://{host}"

        self.client = jenkins.Jenkins(host, username=user, password=api_token)

    def query(self, fn_name, *args, **kwargs):
        """Query the Datsource for job or build data.

        Calls a supported accessor function by name and passthrough any
        positional and keyword arguments.

        Examples::

            # Get a list of all jobs in the Jenkins server
            datasources.query("jenkins", "get_all_jobs")
            # Get detailed information about 'some-job'
            datasources.query("jenkins", "get_job_info", "some-job")

        Args:
            fn_name (str): the RPC operation to invoke.

        Raises:
            ValueError: if an invalid RPC operation is requested.
        """
        fn = getattr(self, fn_name, None)
        if not (fn and callable(fn)):
            raise ValueError(f"No such method {fn_name} for Jenkins client")

        return fn(*args, **kwargs)

    def get_all_jobs(self):
        """List all jobs on the Jenkins server.

        Returns:
            pandas.DataFrame: a DataFrame with columns:

            :fullname: the full job name (will include folder path components)
            :url: a URL that resolves to the job on the Jenkins server
        """
        jobs = pd.DataFrame.from_records(self.client.get_all_jobs())
        # Filter by jobs that don't have child jobs
        leaf_jobs = jobs[jobs.jobs.isna()]
        return leaf_jobs

    def get_job_info(self, job_name):
        """Get a list of builds for a given job, including their statuses.

        Args:
            job_name (str): Full name of the job.

        Returns:
            pandas.DataFrame: a DataFrame with columns:

            :status: the build status, e.g. "SUCCESS" or "FAILURE"
        """
        job_info = self.client.get_job_info(job_name, depth=1)
        builds = job_info.get("builds", [])[:10]
        df = pd.json_normalize(builds)
        # Transpose the health report information into our result table--
        # this is a bit of a hack, but DataFrames need to have columnar data,
        # and this avoids having to create another RPC method just for this.
        health_report = next(iter(job_info.get("healthReport", [])), {})
        return df.assign(**health_report)
