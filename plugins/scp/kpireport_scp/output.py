import logging
import shlex
import tarfile
import tempfile

import fabric
from kpireport_static import StaticOutputDriver

LOG = logging.getLogger(__name__)


class SCPOutputDriver(StaticOutputDriver):
    def init(self, **kwargs):
        self.remote_path = kwargs.pop("remote_path", None)
        self.remote_path_owner = kwargs.pop("remote_path_owner", None)
        self.remote_path_group = kwargs.pop("remote_path_group", None)
        self.sudo = kwargs.pop("sudo", False)
        self.sudo_password = kwargs.pop("sudo_password", None)

        host = kwargs.pop("host", None)

        if not (host and self.remote_path):
            raise ValueError("'host' and 'remote_path' are required")

        if self.sudo is True:
            kwargs.setdefault(
                "config",
                fabric.Config(overrides=dict(sudo=dict(password=self.sudo_password))),
            )

        self.connection = fabric.Connection(host=host, **kwargs)
        self._scp_tmp_dir = tempfile.TemporaryDirectory()

        super(SCPOutputDriver, self).init(output_dir=self._scp_tmp_dir.name)

    def render_output(self, content, blobs):
        super(SCPOutputDriver, self).render_output(content, blobs)

        c = self.connection

        if self.sudo is True:
            run = getattr(c, "sudo")
        else:
            run = getattr(c, "run")

        tarball = f"{self._scp_tmp_dir.name}/{self.report.id}.tar.gz"
        with tarfile.open(tarball, "w:gz") as tar:
            tar.add(self.output_dir, arcname="static")
        remote_tarball = "/tmp/kpireport.tar.gz"
        c.put(tarball, remote=remote_tarball)

        safe_path = shlex.quote(self.remote_path)

        run(f"mkdir -p {safe_path}")
        run(f"tar -xf {remote_tarball} -C {safe_path} --strip-components=1")
        run(f"rm -f {remote_tarball}")

        if self.remote_path_owner:
            safe_owner = shlex.quote(self.remote_path_owner)
            if self.remote_path_group:
                safe_group = shlex.quote(self.remote_path_group)
            else:
                safe_group = ""
            run(f"chown -R {safe_owner}:{safe_group} {safe_path}")

        self._scp_tmp_dir.cleanup()
