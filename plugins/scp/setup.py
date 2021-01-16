from setuptools import setup

setup(
    name="kpireport-scp",
    version="0.0.2",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_scp"],
    install_requires=["kpireport", "kpireport-static", "fabric"],
    entry_points={
        "kpireport.output": ["scp = kpireport_scp:SCPOutputDriver"],
    },
)
