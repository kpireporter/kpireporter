from setuptools import setup

setup(
    name="kpireport-table",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_table"],
    install_requires=[
        "kpireport",
    ],
    entry_points={
        "kpireport.view": ["table = kpireport_table:TableView"],
    },
)
