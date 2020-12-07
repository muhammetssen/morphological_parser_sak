#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
from distutils.spawn import find_executable
import os
from setuptools.command.install import install
import subprocess

with open("README.md", "r") as f:
    long_description = f.read()

with open(os.path.join("morphological_parser_sak", "version.txt"), "r") as f:
    __version__ = f.read().strip()

with open(os.path.join("morphological_parser_sak", 
                        "python_requirements.txt"), "r") as f:
    requirements_list = []
    #requirements_list = [d for d in f.read().split("\n") if d]


class SetupDeps(install):
    
    def run(self):
        print("?"*15)
        if find_executable("perl") is None:
            raise RuntimeError("Perl must be installed on the system")
        pdep_folder = os.path.join("morphological_parser_sak", 
                                        "perl_dependencies")
        wd = os.getcwd()
        os.chdir(pdep_folder)
        output = subprocess.check_output(["bash", "INSTALL.sh"])
        os.chdir(wd)
        install.run(self)


setuptools.setup(
    name="morphological_parser_sak",
    version=__version__,
    author="Haşim Sak",
    author_email="tabilab.dip@gmail.com",
    description="Morphological Parser and Disambiguator with Python Bindings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tabilab-dip/morphological_parser_sak",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
    cmdclass={
        "install": SetupDeps
    },
    package_data={
        "morphological_parser_sak": [
            "perl_dependencies/*",
            "perl_dependencies/*/*",
            "perl_dependencies/*/*/*",
            "perl_dependencies/*/*/*/*",
            "perl_dependencies/*/*/*/*/*",
            "perl_dependencies/*/*/*/*/*/*",
            "perl_dependencies/*/*/*/*/*/*/*",
            "perl_dependencies/*/*/*/*/*/*/*/*",
            "md.pl",
            "model.txt",
            "turkish.fst",
        ]
    },
    exclude_package_data={ # we don't need api for packaged application
        "morphological_parser_sak": [
            "api.py",
        ]
    },
    install_requires=requirements_list,
    python_requires='>=3.6',
)
