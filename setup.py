# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='dualis',
    version='0.0.1',
    description='This is a set of python scripts to scrape grades from dualis.dhbw.de',
    long_description=readme,
    author='Markus Bilz',
    author_email='github@markusbilz.com',
    url='https://github.com/karelze/dualis',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

