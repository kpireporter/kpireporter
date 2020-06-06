import jenkins
import pandas as pd

from kpireport.datasource import Datasource


class JenkinsDatasource(Datasource):
    """Provides accessors for listing all jobs and builds from a Jenkins host.

    The Jenkins Datasource exposes an RPC-like interface to fetch all jobs,
    as well as job details for each job. The plugin will call the Jenkins API
    at the host specified using a username and API token provided as
    plugin arguments.
    """
    def init(self, host=None, user=None, api_token=None):
        """Initialize the Jenkins Datasource.

        :type host: str
        :param host: the Jenkins host, e.g. https://jenkins.example.com
        :type user: str
        :param user: the Jenkins user to authenticate as
        :type api_token: str
        :param api_token: the Jenkins user API token to authenticate with
        """
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

        :type fn_name: str
        :param fn_name: the RPC operation to invoke
        :raise ValueError: if an invalid RPC operation is requested
        """
        fn = getattr(self, fn_name, None)
        if not (fn and callable(fn)):
            raise ValueError(f"No such method {fn_name} for Jenkins client")

        return fn(*args, **kwargs)

    def get_all_jobs(self):
        """List all jobs on the Jenkins server

        :returns: a table with columns:

          :fullname: the full job name (will include folder path components)
          :url: a URL that resolves to the job on the Jenkins server

        :rtype: pandas.DataFrame
        """
        jobs = pd.DataFrame.from_records(self.client.get_all_jobs())
        # Filter by jobs that don't have child jobs
        leaf_jobs = jobs[jobs.jobs.isna()]
        return leaf_jobs

    def get_job_info(self, job_name):
        """
        Get a list of builds for a given job, including their statuses.

        :type job_name: str
        :param job_name: the full name of the job
        :returns: a table with the following columns:

            :status: the build status, e.g. "SUCCESS" or "FAILURE"

        :rtype: pandas.DataFrame
        """
        job_info = self.client.get_job_info(job_name, depth=1)
        df = pd.json_normalize(job_info, "builds")
        # Transpose the health report information into our result table--
        # this is a bit of a hack but it avoids having to make two calls
        # to our datasource (DataFrames don't handle mixed dict/list data)
        return df.assign(**job_info["healthReport"])
