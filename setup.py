#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from setuptools import setup, find_packages
from djng import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

DESCRIPTION = 'Let Django play well with AngularJS'

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Framework :: Django :: 1.10',
    'Framework :: Django :: 1.11',
]

setup(
    name='django-angular',
    version=__version__,
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jrief/django-angular',
    license='MIT',
    keywords=['django', 'angularjs'],
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['examples', 'docs']),
    include_package_data=True,
)
