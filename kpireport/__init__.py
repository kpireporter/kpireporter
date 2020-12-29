from pkg_resources import resource_listdir, resource_string

from .version import VERSION  # noqa

import logging

LOG = logging.getLogger(__name__)

try:
    license_keys = [
        resource_string(__name__, f"license_keys/{r}")
        for r in resource_listdir(__name__, "license_keys")
    ]
except Exception:
    LOG.error("Failed to read license keys, cannot verify user license.")
    license_keys = []

if __name__ == "__main__":
    from .cmd import run

    run()
