from setuptools import setup

plugin_name = "kpireport_jenkins"

setup(
    # Common
    author="yourname",
    author_email="yourname@email.com",
    description="...",
    license="MIT",
    classifiers=[],
    # Package
    name=plugin_name,
    version="0.0.1",
    packages=[plugin_name],
    install_requires=[
        "kpireport",
        "python-jenkins"
    ],
    package_data={"templates": ["*"]},
    entry_points={
        "kpireport.datasource": [
            "jenkins = kpireport_jenkins:JenkinsDatasource"
        ],
        "kpireport.view": [
            "jenkins.build_summary = kpireport_jenkins:JenkinsBuildSummary"
        ]
    }
)