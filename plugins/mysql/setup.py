from setuptools import setup

setup(
    name="kpireport-mysql",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_mysql"],
    install_requires=["kpireport", "mysqlclient"],
    entry_points={
        "kpireport.datasource": ["mysql = kpireport_mysql:MySQLDatasource"],
    },
)
