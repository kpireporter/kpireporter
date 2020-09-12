from setuptools import setup

setup(
    name="kpireport-smtp",
    version="0.0.1",
    author="Jason Anderson",
    author_email="diurnalist@gmail.com",
    license="Prosperity Public License",
    packages=["kpireport_smtp"],
    install_requires=["kpireport", "premailer"],
    entry_points={
        "kpireport.output": ["smtp = kpireport_smtp:SMTPOutputDriver"],
    },
)
