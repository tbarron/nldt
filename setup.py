from setuptools import setup
import version

setup(name='nldt',
      version=version._version,
      description="Natural Language Dates and Times",
      author="Tom Barron",
      author_email='tusculum@gmail.com',
      url='https://github.com/tbarron/nldt',
      packages=['nldt'],
      entry_points={'console_scripts': ['nldt = cmdl:main']}
      )
