from datetime import datetime
from jinja2 import Environment, ChoiceLoader, FileSystemLoader, PackageLoader


def module_root(module_str):
    return module_str.split(".")[0]


def create_jinja_environment(theme: "~kpireport.report.Theme"):
    def datetime_format(value):
        return datetime.strftime(value, "%b %d")

    env = Environment(loader=create_jinja_loader(theme), autoescape=True)
    env.filters["datetimeformat"] = datetime_format

    return env


def create_jinja_loader(theme: "~kpireport.report.Theme"):
    package_loader = PackageLoader(module_root(__name__))

    if theme.theme_dir:
        return ChoiceLoader([FileSystemLoader(theme.theme_dir), package_loader])
    else:
        return package_loader
