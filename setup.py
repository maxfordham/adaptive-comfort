#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "click>=7.0",
    "python==3.4.5",
    "numpy>=1.14.0",
    "pandas>=0.20.3",
    "xlsxwriter>=3.0.3",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Oliver James Hensby",
    author_email="o.hensby@maxfordham.com",
    python_requires=">=3.4.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    description="This package assesses the thermal comfort of a space within a building against the Criterion defined in CIBSE TM52 and TM59.",
    entry_points={"console_scripts": ["adaptive_comfort=adaptive_comfort.cli:main",],},
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="adaptive_comfort",
    name="adaptive_comfort",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/maxfordham/adaptive-comfort",
    version="0.1.1",
)
