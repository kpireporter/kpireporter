from setuptools import setup

setup(
    name="kpireport-prometheus",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_prometheus"],
    install_requires=[
        "kpireport",
        "requests"
    ],
    entry_points={
        "kpireport.datasource": [
            "prometheus = kpireport_prometheus.datasource:PrometheusDatasource"
        ],
        "kpireport.view": [
            "prometheus.alert_summary = kpireport_prometheus.alert_summary:PrometheusAlertSummary"
        ],
    }
)
