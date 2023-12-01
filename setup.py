"""
Package description.

setup.py template shared by Alexander Guckenberger.

"""

import re
import subprocess
from shutil import which
from setuptools import setup, find_packages

NAME = "aoc2023"
VERSION = "0.0.1"
AUTHOR = "Ben Hubbard"
AUTHOR_EMAIL = "brhubbar@mtu.edu"
DESCRIPTION = ""
URL = "https://github.com/brhubbar/advent-of-py-2023"
REQUIREMENTS = {
    "requirements": [],
    "requirements-dev": [
        "coverage",
        "flake8",
        "flake8-docstrings",
        "flake8-annotations",
        "pytest",
    ],
    "requirements-docs": [],
}

LONG_DESCRIPTION = ""



setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=REQUIREMENTS["requirements"],
    extras_require={
        "dev": REQUIREMENTS["requirements-dev"],
        "docs": REQUIREMENTS["requirements-docs"],
    },
    include_package_data=True,
)
