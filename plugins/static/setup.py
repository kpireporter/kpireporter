from setuptools import setup

setup(
    name="kpireport-static",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_static"],
    install_requires=[
        "kpireport",
    ],
    entry_points={
        "kpireport.output": ["static = kpireport_static:StaticOutputDriver"],
    },
)
