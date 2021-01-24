from setuptools import setup

setup(
    name="kpireport-static",
    version="0.0.2",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_static"],
    install_requires=[
        "kpireport",
    ],
    entry_points={
        "kpireport.output": ["static = kpireport_static:StaticOutputDriver"],
    },
)
