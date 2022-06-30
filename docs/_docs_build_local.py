"""
THIS FILE BUILDS THE DOCS LOCALLY USING JUPYTERBOOK AND SPHINX
# you must have a file called "GITHUB_TOKEN" in this 
# dir with nothing but your personal Github token inside
# this file is unique per user and will be ignored by Git
"""

import subprocess
import pathlib
import os

GITHUB_TOKEN = pathlib.Path('GITHUB_TOKEN').read_text()
CONF = pathlib.Path('conf.py')

env = os.environ.copy()
env['SPHINX_GITHUB_CHANGELOG_TOKEN '] = GITHUB_TOKEN
# ^ add SPHINX_GITHUB_CHANGELOG_TOKEN to environ

subprocess.call('jupyter-book config sphinx .', shell=True)
# ^ create `conf.py` file

_conf = CONF.read_text().split('\n')
_conf = _conf + ['import os'] + ['sphinx_github_changelog_token = os.environ.get("SPHINX_GITHUB_CHANGELOG_TOKEN")']
CONF.write_text("\n".join(_conf))
# ^ udpate `conf.py` file

subprocess.call('sphinx-build . _build/html -b html', shell=True, env=env)
# ^ call sphinx build with required environ vars
