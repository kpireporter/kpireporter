from datetime import datetime, timedelta

from reportcard.datasource import DatasourceManager
from reportcard.view import ViewManager


class Report:
    def __init__(self, date_from=None, date_to=None):
        self.date_from = date_from
        self.date_to = date_to


class ReportFactory:
    def __init__(self, config):
        datasource_conf = config.get("datasources", {})
        view_conf = config.get("views", [])

        interval = config.get("interval_days", 7)
        now = datetime.now()
        report = Report(date_from=now - timedelta(days=interval),
                        date_to=now)
                        
        self.dm = DatasourceManager(datasource_conf, report=report)
        self.vm = ViewManager(view_conf, report=report)

    def create(self):
        return self.vm.render(self.dm)
                