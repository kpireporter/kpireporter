from setuptools import setup

setup(
    name="kpireport-mysql",
    version="0.0.1",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_mysql"],
    install_requires=["kpireport", "PyMySQL"],
    entry_points={
        "kpireport.datasource": ["mysql = kpireport_mysql:MySQLDatasource"],
    },
)
