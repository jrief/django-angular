from distutils.core import setup
from distutils.core import Command


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        from django.core.management import call_command
        settings.configure(DATABASES={'default': {'NAME': ':memory:',
            'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=('djangular',))
        call_command('test', 'djangular')


setup(name='djangular',
      version='0.1.0',
      packages=[],
      license='MIT',
      long_description="Mixins classes and helper functions which help to integrate AngularJS with Django.",
      cmdclass={'test': TestCommand}
)
