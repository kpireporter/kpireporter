from datetime import datetime
from jinja2 import Environment, ChoiceLoader, PackageLoader


def module_root(module_str):
    return module_str.split(".")[0]


def create_jinja_environment():
    def datetime_format(value):
        return datetime.strftime(value, "%b %d")

    env = Environment(loader=create_jinja_loader(), autoescape=True)
    env.filters["datetimeformat"] = datetime_format

    return env


def create_jinja_loader(module_paths: list = []):
    if not module_paths:
        module_paths = [__name__]

    if len(module_paths) > 1:
        return ChoiceLoader([PackageLoader(module_root(p)) for p in module_paths])
    else:
        return PackageLoader(module_root(module_paths[0]))
