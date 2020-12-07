from setuptools import setup

setup(
    name="kpireport-table",
    version="0.0.1",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_table"],
    install_requires=[
        "kpireport",
        "tabulate",
    ],
    entry_points={
        "kpireport.view": ["table = kpireport_table:Table"],
    },
)
