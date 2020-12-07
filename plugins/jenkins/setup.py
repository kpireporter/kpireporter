from setuptools import setup

setup(
    name="kpireport-jenkins",
    version="0.0.1",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_jenkins"],
    install_requires=["kpireport", "python-jenkins"],
    package_data={"kpireport_jenkins": ["templates/*"]},
    entry_points={
        "kpireport.datasource": ["jenkins = kpireport_jenkins:JenkinsDatasource"],
        "kpireport.view": [
            "jenkins.build_summary = kpireport_jenkins:JenkinsBuildSummary"
        ],
    },
)
