import setuptools
import os
with open("README.md", "r") as f:
    long_description = f.read()

with open(os.path.join("morphological_parser_sak", "version.txt"), "r") as f:
    __version__ = f.read().strip()

with open(os.path.join("morphological_parser_sak", 
                        "python_requirements.txt"), "r") as f:
    requirements_list = [d for d in f.read().split("\n") if d]

setuptools.setup(
    name="Turkish Morphological Parser and Disambiguator", # Replace with your own username
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
    install_requires=requirements_list,
    python_requires='>=3.6',
)