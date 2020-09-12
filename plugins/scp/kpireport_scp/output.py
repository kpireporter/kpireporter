import fabric
import shlex
import tarfile
import tempfile

from kpireport_static import StaticOutputDriver

import logging

LOG = logging.getLogger(__name__)


class SCPOutputDriver(StaticOutputDriver):
    def init(self, **kwargs):
        self.remote_path = kwargs.pop("remote_path", None)
        self.remote_path_owner = kwargs.pop("remote_path_owner", None)
        self.remote_path_group = kwargs.pop("remote_path_group", None)
        self.sudo = kwargs.pop("sudo", False)
        self.sudo_password = kwargs.pop("sudo_password", None)

        if not self.remote_path:
            raise ValueError("'remote_path' is required")

        if self.sudo is True:
            kwargs.setdefault(
                "config",
                fabric.Config(overrides=dict(sudo=dict(password=self.sudo_password))),
            )

        self.connection = fabric.Connection(**kwargs)
        self.tmp_dir = tempfile.TemporaryDirectory()

        super(SCPOutputDriver, self).init(output_dir=self.tmp_dir.name)

    def render_output(self, content, blobs):
        super(SCPOutputDriver, self).render_output(content, blobs)

        c = self.connection

        if self.sudo is True:
            run = getattr(c, "sudo")
        else:
            run = getattr(c, "run")

        with self.tmp_dir as tmp_dir:
            tarball = f"{self.report.id}.tar.gz"
            with tarfile.open(tarball, "w:gz") as tar:
                tar.add(tmp_dir, arcname="static")
            try:
                remote_tarball = "/tmp/kpireport.tar.gz"
                c.put(tarball, remote=remote_tarball)

                safe_path = shlex.quote(self.remote_path)

                run(
                    (f"tar -xf {remote_tarball} -C {safe_path} " "--strip-components=1")
                )
                run(f"rm -rf {remote_tarball}")

                if self.remote_path_owner:
                    safe_owner = shlex.quote(self.remote_path_owner)
                    if self.remote_path_group:
                        safe_group = shlex.quote(self.remote_path_group)
                    else:
                        safe_group = ""
                    run(f"chown -R {safe_owner}:{safe_group} {safe_path}")
            except Exception as e:
                LOG.error(f"Error copying file to remote host: {e}")
