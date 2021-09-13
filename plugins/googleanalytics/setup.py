from setuptools import setup

setup(
    name="kpireport-googleanalytics",
    version="0.0.2",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_googleanalytics"],
    install_requires=["kpireport", "google-api-python-client", "oauth2client", "pytz"],
    entry_points={
        "kpireport.datasource": [
            "googleanalytics = kpireport_googleanalytics:GoogleAnalyticsDatasource"
        ],
    },
)
