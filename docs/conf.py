# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from datetime import datetime
from io import BytesIO
import os
import shutil
from zipfile import ZipFile

import requests

from kpireport import VERSION


# -- Project information -----------------------------------------------------

module_name = "kpireport"
project = "kpireport"
copyright = "2020, Jason Anderson"
author = "Jason Anderson"

release = VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx-jsonschema",
    "sphinx_rtd_theme",
    "sphinxcontrib.napoleon",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "boto3": (
        "https://boto3.amazonaws.com/v1/documentation/api/latest/index.html",
        "https://boto3.amazonaws.com/v1/documentation/api/latest/objects.inv",
    ),
    "pandas": (
        "http://pandas.pydata.org/pandas-docs/stable/",
        "http://pandas.pydata.org/pandas-docs/stable/objects.inv",
    ),
    "pymysql": (
        "https://pymysql.readthedocs.io/",
        "https://pymysql.readthedocs.io/page/objects.inv",
    ),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "logo_only": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = "_static/img/kpireporter_logo.svg"

html_css_files = ["css/custom.css"]

html_extra_path = ["_extra"]

# Copy schema file(s)
os.makedirs("_extra", exist_ok=True)
shutil.copy("../schema/configuration.schema.json", "_extra/")


def artifact_sort(artifact):
    return datetime.strptime(artifact.get("created_at"), "%Y-%m-%dT%H:%M:%S%z")


gh_api_base = "https://api.github.com"
gh_repo = os.getenv("GITHUB_REPOSITORY")
gh_token = os.getenv("GITHUB_TOKEN")

try:
    if not (gh_repo and gh_token):
        raise ValueError("Missing GitHub environment variables")

    gh_artifacts_url = f"{gh_api_base}/repos/{gh_repo}/actions/artifacts"
    if gh_token:
        gh_auth = ("admin", gh_token)
    else:
        gh_auth = None

    res = requests.get(gh_artifacts_url)

    res.raise_for_status()
    artifacts = res.json().get("artifacts")
    latest = next(iter(sorted(artifacts, key=artifact_sort, reverse=True)), None)
    if latest:
        zip_res = requests.get(
            f"{gh_artifacts_url}/{latest.get('id')}/zip", auth=gh_auth
        )
        zip_res.raise_for_status()
        zipfile = ZipFile(BytesIO(zip_res.content))
        zipfile.extractall("_extra/examples")
except Exception as e:
    print("Unable to fetch GHA artifacts: ", e)


# Mock all the extra_requires modules. Without this, Sphinx cannot
# generate documentation via autodoc unless the relevant dependencies
# are explicitly installed, which we don't want to require. It is fine
# to mock the extra dependencies here.
autodoc_mock_imports = ["boto3", "jenkins", "MySQLdb"]
