"""setup.py install runs this file"""

import distutils.command.build_py as orig
import os

from setuptools import find_packages, setup

NAME = "src"
VERSION_REQUIREMENT = 3.7


with open("requirements.txt", "r") as f:
    REQUIREMENTS = f.read().split("\n")


with open("test-requirements.txt", "r") as f:
    TEST_REQUIREMENTS = f.read().split("\n")


def package_files(package, directory):
    paths = []
    for (path, _, filenames) in os.walk(os.path.join(package, directory)):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

if __name__ == "__main__":
    
    setup(
        name=NAME,
        version="1.0.0",
        maintainer="0xfMissingNo.",
        maintainer_email="0xfMissingNo@gmail.com",
        description="Uatu",
        url="git@github.com:0xfMissingNo/Uatu.git",
        package_dir={"": NAME},
        packages=find_packages(NAME, exclude=["tests*"]),
        python_requires=">={}".format(VERSION_REQUIREMENT),
        install_requires=REQUIREMENTS + TEST_REQUIREMENTS,
        package_data={NAME: package_files(NAME, ".")},
        cmdclass={
            "build_py": orig.build_py
            },
        entry_points={
            "console_scripts": []
        }
    )