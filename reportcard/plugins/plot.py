from reportcard.view import View


class Plot(View):
    def render(self, datasources, theme=None):
        ds = self.get("datasource")
        data = None

        if ds:
            query = self.get("query")
            if not query:
                raise ValueError("Missing query for datasource")
            data = datasources.query(ds, query)


class SingleStat(View):
    def render(self, datasources, theme=None):
        pass
