from distutils.core import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='django-view-extractor',
    version='0.1.0',
    packages=setuptools.find_packages(),
    url='https://www.quickrelease.co.uk',
    license='GNU GPLv3',
    author='Nick Solly',
    author_email='nick.solly@quickrelease.co.uk',
    description='Extract Django views, urls and permissions',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'tabulate==0.8.6',
    ],
)
