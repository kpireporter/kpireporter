from jinja2 import Markup
import shutil
import os

from reportcard.output import OutputDriver

import logging
LOG = logging.getLogger(__name__)


class StaticOutputDriver(OutputDriver):
    def init(self, output_dir="_build/static"):
        self.output_dir = output_dir

    def render_blob_inline(self, blob):
        return Markup(f"""<img src="{blob["id"]}" />""")

    def render_output(self, content, blobs):
        content = content.get("html")
        report_dir = os.path.join(self.output_dir, self.report.id)
        latest_dir = os.path.join(
            self.output_dir,
            f"latest-{self.report.title_slug}")

        os.makedirs(report_dir, exist_ok=True)
        with open(os.path.join(report_dir, "index.html"), "w") as f:
            f.write(content)

        for blob in blobs:
            blob_path = os.path.join(report_dir, blob["id"])
            os.makedirs(os.path.dirname(blob_path), exist_ok=True)
            with open(blob_path, "wb") as f:
                f.write(blob["content"].getvalue())

        try:
            shutil.copytree(report_dir, latest_dir, dirs_exist_ok=True)
        except Exception:
            LOG.exception("Error saving latest report")
