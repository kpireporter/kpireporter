from jinja2 import Markup
import shutil
import os

from kpireport.output import OutputDriver

import logging

LOG = logging.getLogger(__name__)


class StaticOutputDriver(OutputDriver):
    """Export a report's HTML contents to disk.

    Attributes:
        output_dir (str): the directory to output the report HTML contents to.
            (Default ``"./_build"``)
    """

    def init(self, output_dir="_build"):
        self.output_dir = output_dir

    def render_blob_inline(self, blob, fmt=None):
        if fmt == "md":
            return f"""![{blob.title}]({blob.id})"""
        else:
            return Markup(f"""<img src="{blob.id}" />""")

    def render_output(self, content, blobs):
        content = content.get_format("html")
        report_dir = os.path.join(self.output_dir, self.report.id)
        latest_dir = os.path.join(self.output_dir, f"latest-{self.report.title_slug}")

        os.makedirs(report_dir, exist_ok=True)
        with open(os.path.join(report_dir, "index.html"), "w") as f:
            f.write(content)

        for blob in blobs:
            blob_path = os.path.join(report_dir, blob.id)
            os.makedirs(os.path.dirname(blob_path), exist_ok=True)
            with open(blob_path, "wb") as f:
                f.write(blob.content.getvalue())

        try:
            os.makedirs(latest_dir, exist_ok=True)
            try:
                shutil.copytree(report_dir, latest_dir, dirs_exist_ok=True)
            except TypeError:
                # On Python < 3.8, where dirs_exist_ok parameter doesn't exist.
                _copytree(report_dir, latest_dir)
        except Exception:
            LOG.exception("Error saving latest report")


def _copytree(src, dst, symlinks=False, ignore=None):
    """Shimmed shutils.copytree that handles directories already existing.

    Credit: https://stackoverflow.com/a/12514470/493110

    NOTE(jason): Remove when support for Python <3.8 is dropped.
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            _copytree(s, d, symlinks, ignore)
        else:
            os.makedirs(dst, exist_ok=True)
            shutil.copy2(s, d)
