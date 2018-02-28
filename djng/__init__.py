# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
See PEP 386 (https://www.python.org/dev/peps/pep-0386/)

Release logic:
 1. Remove ".devX" from __version__ (below)
 2. Remove ".devX" latest version in docs/changelog.rst
 3. git add djng/__init__.py
 4. git commit -m 'Bump to <version>'
 5. git push
 6. assure that all tests pass on https://travis-ci.org/jrief/django-angular
 7. git tag <version>
 8. git push --tags
 9. python setup.py sdist upload
10. bump the version, append ".dev0" to __version__
11. Add a new heading to docs/changelog.rst, named "<next-version>.dev0"
12. git add djng/__init__.py docs/changelog.rst
12. git commit -m 'Start with <version>'
13. git push
"""

__version__ = '2.0.2'

default_app_config = 'djng.app_config.DjangoAngularConfig'
