from jinja2 import Markup
import os

from reportcard.output import OutputDriver


class HTMLOutputDriver(OutputDriver):
    def init(self, output_dir="_build/html"):
        self.output_dir = output_dir

    def render_blob_inline(self, blob):
        return Markup(f"""<img src="{blob["id"]}" />""")

    def render_output(self, content, blobs):
        content = content.get("html")

        os.makedirs(self.output_dir, exist_ok=True)
        with open(os.path.join(self.output_dir, "index.html"), "w") as f:
            f.write(content)

        for blob in blobs:
            blob_path = os.path.join(self.output_dir, blob["id"])
            os.makedirs(os.path.dirname(blob_path), exist_ok=True)
            with open(blob_path, "wb") as f:
                f.write(blob["content"].getvalue())
