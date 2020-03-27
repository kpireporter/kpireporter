import io
import matplotlib.pyplot as plt

from reportcard.view import View


class Plot(View):
    def init(self, datasource=None, query=None):
        self.datasource = datasource
        self.query = query

        if not (self.datasource and self.query):
            raise ValueError((
                "Both a 'datasource' and 'query' parameter are required"))

    def render(self):
        df = self.datasources.query(self.datasource, self.query)

        fig, ax = plt.subplots(nrows=1, ncols=1)
        df.plot(ax=ax)

        figbytes = io.BytesIO()
        fig.savefig(figbytes)
        figname = "figure.png"
        self.add_blob(figname, figbytes)

        plt.close(fig)

        template = self.j2.get_template("plot.html")

        return template.render(figure=figname)


class SingleStat(View):
    def init(self, **kwargs):
        pass
    
    def render(self):
        pass
