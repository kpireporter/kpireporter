import fabric
import tempfile

from reportcard.plugins.static import StaticOutputDriver

import logging
LOG = logging.getLogger(__name__)


class SCPOutputDriver(StaticOutputDriver):
    def init(self, **kwargs):
        self.remote_path = kwargs.pop("remote_path", None)

        if not self.remote_path:
            raise ValueError("'remote_path' is required")

        self.connection = fabric.Connection(**kwargs)
        self.tmp_dir = tempfile.TemporaryDirectory()

        super(SCPOutputDriver, self).init(output_dir=self.tmp_dir)

    def render_output(self, content, blobs):
        super(SCPOutputDriver, self).render_output(content, blobs)

        try:
            self.connection.put(self.tmp_dir, remote=self.remote_path)
        except Exception as e:
            LOG.error(f"Error copying file to remote host: {e}")
        finally:
            self.tmp_dir.cleanup()
