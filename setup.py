import os
import pathlib
import shutil
from io import open
from os import environ, path

import pkg_resources
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
with open(path.join(HERE, "README.md")) as f:
    README = f.read()

# automatically captured required modules for install_requires in requirements.txt and as well as configure dependency links
with open(path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")
install_requires = [
    x.strip()
    for x in all_reqs
    if ("git+" not in x) and (not x.startswith("#")) and (not x.startswith("-"))
]
dependency_links = [x.strip().replace("git+", "") for x in all_reqs if "git+" not in x]

setup(
    name="printop",
    description="pretty print evm opcodes from a given solidity contract",
    version="0.1.0",
    package_dir={"": "."},
    packages=[
        "src"
    ],  # list of all packages
    install_requires=install_requires,
    python_requires=">=3.7",  # any python greater than 3.7
    entry_points="""
        [console_scripts]
        printop=src.Disasm:main
    """,
    author="bitbasebit",
    keyword="evm, ethereum, evm toosl",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/BitBaseBit/opcode_pretty",
    download_url="",
    dependency_links=dependency_links,
    author_email="vardygreg23@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
)
