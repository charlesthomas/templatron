from setuptools import setup, find_packages
from sys import path

from templatron import __version__

NAME = "templatron"
if __name__ == "__main__":

    with open('requirements.txt') as f:
        REQS = f.read().splitlines()

    setup(
        name=NAME,
        version=__version__,
        author="Charles Thomas",
        author_email="ch@rlesthom.as",
        url="https://github.com/charlesthomas/templatron",
        license='ASLv2',
        packages=find_packages(),
        package_dir={NAME: NAME},
        description="sync templated common files across repos",
        install_requires=REQS,
        entry_points={
            'console_scripts': [
                'templatron = templatron.cli:main',
                'tt = templatron.cli:main',
            ],
        }
    )
