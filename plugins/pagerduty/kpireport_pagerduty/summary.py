from kpireport.view import View


class PagerDutySummary(View):
    """Display a summary of incidents on a PagerDutyAccount."""

    def init(self, **kwargs):
        return super().init(**kwargs)
