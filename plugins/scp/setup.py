from setuptools import setup

setup(
    name="kpireport-scp",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_scp"],
    install_requires=["kpireport", "kpireport-static", "fabric"],
    entry_points={
        "kpireport.output": ["scp = kpireport_scp:SCPOutputDriver"],
    },
)
