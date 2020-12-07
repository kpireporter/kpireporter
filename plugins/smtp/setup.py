from setuptools import setup

setup(
    name="kpireport-smtp",
    version="0.0.1",
    author="KPI Reporter LLC",
    author_email="dev@kpireporter.com",
    license="Prosperity Public License",
    packages=["kpireport_smtp"],
    install_requires=["kpireport", "premailer"],
    entry_points={
        "kpireport.output": ["smtp = kpireport_smtp:SMTPOutputDriver"],
    },
)
