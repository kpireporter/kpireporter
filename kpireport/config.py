import os
import re
import yaml

DEFAULT_CONF_DIR = "/etc/kpireporter"

path_matcher = re.compile(r".*\$\{([^}^{]+)\}.*")


def path_constructor(loader, node):
    return os.path.expandvars(node.value)


# Declare custom YAML loader that can interpolate
# environment variables
class EnvAwareLoader(yaml.SafeLoader):
    pass


EnvAwareLoader.add_implicit_resolver("!path", path_matcher, None)
EnvAwareLoader.add_constructor("!path", path_constructor)


def load(*files) -> dict:
    def merge(src, dst):
        """Deep merge two dictionaries. Doesn't handle merging lists."""
        for k, v in src.items():
            if isinstance(v, dict):
                merge(v, dst.setdefault(k, {}))
            else:
                dst[k] = v
        return dst

    conf = dict()
    for f in files:
        merge(yaml.load(f, Loader=EnvAwareLoader), conf)
        f.close()

    conf.setdefault("title", "Status report {from}-{to}")
    conf.setdefault("theme", {})
    conf.setdefault("datasources", {})
    conf.setdefault("views", {})
    conf.setdefault("outputs", {"static": {"plugin": "static"}})

    return conf
