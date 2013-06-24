from setuptools import setup, find_packages

DESCRIPTION = 'Mixins classes and helper functions which help to integrate AngularJS with Django.'

try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name='django-angular',
    version='0.1.3',
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/jrief/django-angular',
    license='MIT',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=['Django>=1.4'],
    packages=find_packages(exclude=["tests", "docs"]),
    include_package_data=True,
    zip_safe=False
)
