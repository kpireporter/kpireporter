from setuptools import setup

setup(
    name="kpireport-plot",
    version="0.3.1",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
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
