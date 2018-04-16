#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Laptop'
__date__ = '2018-04-15'
__description__ = " "
__version__ = '1.7'

import os
from distutils.core import setup

from setuptools import find_packages

install_reqs = []

this_dir, this_filename = os.path.split(__file__)
print(this_dir)
DATA_PATH = os.path.join(this_dir, 'hydsensread', "file_example", '*.*')
print(DATA_PATH)
with open('requirements.txt', 'r') as f:
    for lines in f.readlines():
        install_reqs.append(lines.replace('\n', ''))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='HydroSensorReader',
      version=__version__,
      description='Contain files readers for specific sensors files',
      author=__author__,
      author_email='maletxa@gmail.com',
      url='https://github.com/x-malet/scientific_file_reader',
      packages=find_packages(),
      package_data={'hydsensread': [DATA_PATH]},
      install_requires=install_reqs,
      license='GPLv3',
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Natural Language :: French',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Database']
      )