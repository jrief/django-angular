import os
import json
from setuptools import setup, find_packages

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
]


def read(fname):
    readme_file = os.path.join(os.path.dirname(__file__), fname)
    return os.popen('[ -x "$(which pandoc 2>/dev/null)" ] && pandoc -t rst {0} || cat {0}'.format(readme_file)).read()

with open('client/package.json', 'r') as fp:
    package = json.load(fp)

setup(
    name=package['name'],
    version=package['version'],
    author=package['author']['name'],
    author_email=package['author']['email'],
    description=package['description'],
    long_description=read('README.md'),
    url=package['homepage'],
    license=package['license'],
    keywords=package['keywords'],
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['examples', 'docs']),
    include_package_data=True,
    zip_safe=False,
)
