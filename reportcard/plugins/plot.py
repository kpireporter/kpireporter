import io
import matplotlib.pyplot as plt

from reportcard.view import View


class Plot(View):
    def init(self):
        missing = [k for k in ["datasource", "query"] if not self.get(k)]

        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

    def render(self):
        ds = self.get("datasource")
        query = self.get("query")
        df = self.datasources.query(ds, query)

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
    def render(self):
        pass
