from setuptools import setup

setup(
    name="kpireport-slack",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_slack"],
    install_requires=["kpireport", "slackclient"],
    entry_points={
        "kpireport.output": ["slack = kpireport_slack:SlackOutputDriver"],
    },
)
