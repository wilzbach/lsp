#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import subprocess
import sys
from os import path
from shutil import rmtree

from setuptools import Command, find_packages, setup

root_dir = path.dirname(__file__)


# Read a file and return its as a string
def read(file_name):
    return io.open(path.join(root_dir, file_name)).read()


name = "sls"
version = read(path.join("sls", "version.py")).split('"')[1].strip()
description = read("README.md")
short_description = (
    "SLS is the Storyscript Language Server. It provides "
    "common editor features like completion to its clients."
)

classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Environment :: Plugins",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Other Scripting Engines",
    "Topic :: Office/Business",
    "Topic :: Software Development :: Build Tools",
    "Topic :: Software Development :: Code Generators",
]

requirements = [
    "python-jsonrpc-server==0.1.2",
    "storyscript==0.26.2",
    "click~=7.0",
    "click-aliases~=1.0",
    "cachetools~=3.1",
    "tornado~=6.0",
    "sentry_sdk~=0.13",
    "parso==0.5.1",
]


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(path.join(root_dir, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        subprocess.run(
            [
                sys.executable,
                "setup.py",
                "sdist",
                "bdist_wheel",
                "--universal",
            ],
            check=True,
        )

        self.status("Uploading the package to PyPI via Twine…")
        subprocess.run(["twine", "upload", "dist/*"], check=True, shell=True)

        sys.exit()


setup(
    name=name,
    version=version,
    description=short_description,
    long_description=description,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    download_url=(
        "https://github.com/storyscript/sls/archive/" f"{version}.zip"
    ),
    keywords="storyscript language server vscode asyncy",
    author="Storyscript",
    author_email="support@storyscript.io",
    url="https://storyscript.io",
    license="Apache 2.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=requirements,
    python_requires=">=3.7",
    entry_points={"console_scripts": ["sls=sls.cli:Cli.main"]},
    extras_require={
        "stylecheck": ["black==19.10b0"],
        "pytest": [
            "pytest==3.6.3",
            "pytest-cov==2.5.1",
            "pytest-mock==1.10.0",
            "pytest-parallel==0.0.9",
        ],
    },
    cmdclass={"upload": UploadCommand},
)
