#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from os import path

with open('README.md') as readme_file:
    readme = readme_file.read()

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt')) as f:
    requirements = f.read().split()

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Simon Ball",
    author_email='simon.ball@ntnu.no',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="A strain analysis tool written in Pythong",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='strain analysis',
    name='pyedna',
    packages=find_packages(include=['pyedna*']),
    url='https://github.com/simon-ball/PyEdna',
    version='0.1',
    zip_safe=False,
)
