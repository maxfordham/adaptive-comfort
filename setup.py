#!/usr/bin/env python

"""The setup script."""

import versioneer
from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
    )

