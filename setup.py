#!/usr/bin/python3

from rjgtoys.projects import setup


setup(
    name = "rjgtoys.xc",
    version = "0.0.1",
    author = "Bob Gautier",
    author_email = "bob.gautier@gmail.com",
    description = ("Structured exceptions"),
    namespace_packages=['rjgtoys'],
    packages = ['rjgtoys','rjgtoys.xc'],
    install_requires = [
        'pydantic',
    ]
)
