from setuptools import setup

setup(
    name="kpireport-prometheus",
    version="0.0.2",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_prometheus"],
    install_requires=["kpireport", "Pillow", "requests"],
    package_data={"kpireport_prometheus": ["templates/*"]},
    entry_points={
        "kpireport.datasource": [
            "prometheus = kpireport_prometheus:PrometheusDatasource"
        ],
        "kpireport.view": [
            "prometheus.alert_summary = kpireport_prometheus:PrometheusAlertSummary"
        ],
    },
)
