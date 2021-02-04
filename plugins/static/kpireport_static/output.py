import shutil
import tempfile
import os

import imgkit
from jinja2 import Markup

from kpireport.output import OutputDriver

import logging

LOG = logging.getLogger(__name__)


class StaticOutputDriver(OutputDriver):
    """Export a report's contents to disk.

    Attributes:
        output_dir (str): the directory to output the report contents to.
            (Default "./_build")
        output_format (str): The output format, which can be one of "html" or "png".
            (Default "html".) Depending on the format, the output will have a few
            different forms:

            :html: The HTML report will be outputted in a new directory in the output
                path, named after the report. A "latest" directory will also be
                outputted/updated with the contents of this report.
            :png: The report will be rendered as a single PNG image named after the
                report in the output path, and a "latest" PNG will also be outputted.

            .. note::
               ``wkhtmltopdf`` is required if using PNG output. You will probably also
               need to install ``Xvfb`` if using a Docker container that doesn't already
               have an X server packaged.

    """

    def init(self, output_dir="_build", output_format="html"):
        self.output_dir = os.path.abspath(output_dir)
        self.output_format = output_format
        self.tmp_dir = tempfile.TemporaryDirectory()

        self._has_xvfb = shutil.which("Xvfb") is not None

    @property
    def _render_dir(self):
        return self.tmp_dir.name

    def _cleanup(self):
        self.tmp_dir.cleanup()

    def render_blob_inline(self, blob, fmt=None):
        prefix = self._render_dir if self.output_format == "png" else "."
        if fmt == "md":
            return f"""![{blob.title}]({prefix}/{blob.id})"""
        else:
            return Markup(f"""<img src="{prefix}/{blob.id}" />""")

    def render_output(self, content, blobs):
        content = content.get_format("html")

        os.makedirs(self._render_dir, exist_ok=True)

        report_file = os.path.join(self._render_dir, "index.html")
        with open(report_file, "w") as f:
            f.write(content)

        for blob in blobs:
            blob_path = os.path.join(self._render_dir, blob.id)
            os.makedirs(os.path.dirname(blob_path), exist_ok=True)
            with open(blob_path, "wb") as f:
                f.write(blob.content.getvalue())

        if self.output_format == "html":
            output_paths = [
                os.path.join(self.output_dir, self.report.id),
                # Also write to "latest" alias
                os.path.join(self.output_dir, f"latest-{self.report.title_slug}"),
            ]
            for path in output_paths:
                _copy(self._render_dir, path)
        elif self.output_format == "png":
            output_file = os.path.join(self._render_dir, f"{self.report.id}.png")
            theme = self.report.theme
            # It works better to render at a larger width and then
            # crop down, don't ask me why. The fonts render at strange
            # sizes otherwise.
            width = 1024
            crop_width = (theme.num_columns * theme.column_width) + (
                theme.padding_width * 2
            )
            imgkit_options = {
                "width": width,
                # Crop center portion of rendered image
                "crop-x": int((width - crop_width) / 2),
                "crop-w": int(crop_width),
                "crop-y": int(theme.padding_width),
                "format": "png",
            }
            if self._has_xvfb:
                imgkit_options["xvfb"] = ""

            with open(report_file, "r") as f:
                imgkit.from_file(f, output_file, options=imgkit_options)

            output_paths = [
                os.path.join(self.output_dir, f"{self.report.id}.png"),
                os.path.join(self.output_dir, f"latest-{self.report.title_slug}.png"),
            ]
            for path in output_paths:
                _copy(output_file, path)

        self._cleanup()


def _copy(src, dst):
    try:
        if os.path.isfile(src):
            shutil.copy(src, dst)
        elif os.path.isdir(src):
            os.makedirs(dst, exist_ok=True)
            try:
                shutil.copytree(src, dst, dirs_exist_ok=True)
            except TypeError:
                # On Python < 3.8, where dirs_exist_ok parameter doesn't exist.
                LOG.debug("shutil.copytree not available, falling back")
                _copytree(src, dst)
        else:
            raise ValueError("Source is not a file or directory")
    except Exception:
        LOG.exception("Error copying report to output directory")


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
