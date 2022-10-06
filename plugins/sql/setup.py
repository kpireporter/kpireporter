from setuptools import setup

setup(
    name="kpireport-sql",
    version="0.1.0",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_sql"],
    install_requires=["kpireport", "PyMySQL"],
    entry_points={
        "kpireport.datasource": [
            "mysql = kpireport_sql:SQLDatasource",
            "sql = kpireport_sql:SQLDatasource"
        ],
    },
)
