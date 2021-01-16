from setuptools import setup

setup(
    name="kpireport-sendgrid",
    version="0.0.1",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    url="https://kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_sendgrid"],
    install_requires=["kpireport", "premailer", "sendgrid"],
    entry_points={
        "kpireport.output": ["sendgrid = kpireport_sendgrid:SendGridOutputDriver"],
    },
)
