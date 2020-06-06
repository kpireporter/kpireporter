from setuptools import setup

setup(
    name="kpireport-jenkins",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_jenkins"],
    install_requires=[
        "kpireport",
        "python-jenkins"
    ],
    package_data={"templates": ["*"]},
    entry_points={
        "kpireport.datasource": [
            "jenkins = kpireport_jenkins.datasource:JenkinsDatasource"
        ],
        "kpireport.view": [
            "jenkins.build_summary = kpireport_jenkins.build_summary:JenkinsBuildSummary"
        ]
    }
)