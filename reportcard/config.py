import os
import re
import yaml


path_matcher = re.compile(r'.*\$\{([^}^{]+)\}.*')


def path_constructor(loader, node):
    return os.path.expandvars(node.value)


# Declare custom YAML loader that can interpolate
# environment variables
class EnvAwareLoader(yaml.SafeLoader):
    pass


EnvAwareLoader.add_implicit_resolver("!path", path_matcher, None)
EnvAwareLoader.add_constructor("!path", path_constructor)


def load(file) -> dict:
    conf = yaml.load(file, Loader=EnvAwareLoader)

    conf.setdefault("title", "Status report {from}-{to}")
    conf.setdefault("datasources", {})
    conf.setdefault("views", {})
    conf.setdefault("outputs", {
        "html": {
            "plugin": "html"
        }
    })

    return conf
