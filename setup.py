# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from TSGroupAssigner import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='TSGroupAssigner',
    version=__version__,
    url='https://github.com/mightyBroccoli/TSGroupAssigner',
    author='nico wellpott',
    author_email='nico@magicbroccoli.de',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: System Administrators',
        'Operating System :: Unix',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Topic :: Communications",
        "Topic :: Internet"
    ],
    license='GPLv3',
    description='date based TeamSpeak Group Assigner',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='automation TeamSpeak teamspeak ts3 ts3server ts',
    install_requires='ts3>=1.0.11',
    packages=find_packages(exclude=("tests",)),
    python_requires='>=3.6'
)
