from setuptools import setup

setup(
    name="kpireport-plot",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_plot"],
    install_requires=["kpireport", "matplotlib"],
    package_data={"kpireport_plot": ["templates/*"]},
    entry_points={
        "kpireport.view": [
            "plot = kpireport_plot:Plot",
            "single_stat = kpireport_plot:SingleStat",
        ],
    },
)
