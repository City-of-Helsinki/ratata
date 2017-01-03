#!/usr/bin/env python3
from setuptools import setup

install_requires = [
    'colorama',
    'PyYAML',
    'requests',
    'slackclient',
    'grequests',
]

tests_require = [
    'pytest',
]


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='Ratata',
      version='0.2',
      description='Ratata is an API testing and validation tool',
      long_description=readme(),
      install_requires=install_requires,
      tests_require=tests_require,
      setup_requires=['pytest-runner'],
      author='Lauri Kainulainen',
      author_email='lauri@montel.fi',
      url='https://github.com/City-of-Helsinki/ratata',
      packages=['ratata'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Testing',
      ],
      )
