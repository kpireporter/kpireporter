import os
import re
import yaml

# Declare custom YAML loader that can interpolate
# environment variables
class EnvAwareLoader(yaml.SafeLoader):
    pass

path_matcher = re.compile(r'.*\$\{([^}^{]+)\}.*')
def path_constructor(loader, node):
    return os.path.expandvars(node.value)

EnvAwareLoader.add_implicit_resolver("!path", path_matcher, None)
EnvAwareLoader.add_constructor("!path", path_constructor)

def load(file) -> dict:
    conf = yaml.load(file, Loader=EnvAwareLoader)

    conf.setdefault("datasources", {})
    conf.setdefault("views", {})
    
    return conf
