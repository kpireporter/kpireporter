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
    package_data={"templates": ["*"]},
    entry_points={
        "kpireport.view": [
            "plot = kpireport_plot.plot:Plot",
            "single_stat = kpireport_plot.single_stat:SingleStat"
        ],
    }
)
