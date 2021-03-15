"""Setup module for Robot Framework Docker Library package."""

import os

from setuptools import setup

# get absolute source directory path
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    long_description = readme_file.read().split('long_description split')[1].strip()

setup(
    name='robotframework-docker',
    version='1.1.0',
    description='A Robot Framework Docker Library',
    long_description=long_description,
    url='https://github.com/vogoltsov/robotframework-docker',
    author='Vitaly Ogoltsov',
    author_email='vitaly.ogoltsov@me.com',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Robot Framework :: Library',
    ],
    keywords='testing testautomation robotframework docker docker-compose',
    package_dir={'': 'src'},
    py_modules=['DockerComposeLibrary'],
    install_requires=[
        'robotframework>=4,<5',
        'packaging',
    ],
)
