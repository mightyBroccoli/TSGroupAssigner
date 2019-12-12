# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='TSGroupAssigner',
    version='0.0.1',
    packages=find_packages(exclude=['tests', 'tests.*']),
    keywords='automation TeamSpeak teamspeak ts3 ts3server ts',
    url='https://github.com/mightyBroccoli/TSGroupAssigner',
    license='GPLv3',
    author='nico wellpott',
    author_email='nico@magicbroccoli.de',
    description='date based TeamSpeak Group Assigner',
    long_description=long_description,
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: System Administrators',
        'Operating System :: Unix',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ]
)
