from setuptools import setup

setup(
    name="kpireport-slack",
    version="0.0.3",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_slack"],
    install_requires=["kpireport", "slackclient"],
    entry_points={
        "kpireport.output": ["slack = kpireport_slack:SlackOutputDriver"],
    },
)
