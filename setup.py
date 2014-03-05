import os
from setuptools import setup, find_packages
from djangular import __version__

DESCRIPTION = 'Reusable mixins classes and utility functions which help to integrate AngularJS with Django.'

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Development Status :: 4 - Beta',
]


setup(
    name='django-angular',
    version=__version__,
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    description=DESCRIPTION,
    long_description="",
    url='https://github.com/jrief/django-angular',
    license='MIT',
    keywords = ['django', 'angularjs'],
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=['Django>=1.4'],
    packages=find_packages(exclude=['examples', 'docs']),
    include_package_data=True,
)
