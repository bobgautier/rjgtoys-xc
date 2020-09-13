#!/usr/bin/python3

from rjgtoys.projects import setup, readfile


setup(
    name = "rjgtoys-xc",
    version = "0.0.1",
    author = "Robert J Gautier",
    author_email = "bob.gautier@gmail.com",
    url = "https://github.com/bobgautier/rjgtoys-xc",
    description = ("Structured exceptions for Python"),
    namespace_packages=['rjgtoys'],
    packages = ['rjgtoys','rjgtoys.xc'],
    install_requires = [
        'pydantic',
    ],
    extras_require = {
        'autodoc': ['sphinx_autodoc_typehints'],
        'fastapi': ['fastapi>=0.61.1']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
