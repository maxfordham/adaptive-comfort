#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

if __name__ == '__main__':
    setup()

# with open("README.md") as readme_file:
#     readme = readme_file.read()
# 
# 
# requirements = [
#     "pip<19.2",
#     "numpy<=1.14.0",
#     "pandas<=0.20.3",
#     "xlsxwriter<=3.0.3",
# ]
# 
# test_requirements = [
#     "pytest>=3",
# ]
# 
# 
# setup(
#     name="adaptive-comfort",
#     version="0.1.1",
#     author="Oliver James Hensby",
#     author_email="o.hensby@maxfordham.com",
#     description="This package assesses the thermal comfort of a space within a building against the Criterion defined in CIBSE TM52 and TM59.",
#     keywords="adaptive-comfort",
#     url="https://github.com/maxfordham/adaptive-comfort",
#     classifiers=[
#         "Development Status :: 2 - Pre-Alpha",
#         "Intended Audience :: Developers",
#         "Natural Language :: English",
#         "Programming Language :: Python :: 3.4",
#         "Programming Language :: Python :: 3.5",
#     ],
#     install_requires=requirements,
#     package_dir={"": "src"},
#     packages=find_packages(where="src"),
#     python_requires="==3.4.5",
#     test_suite="tests",
#     tests_require=test_requirements,
#     
# )
