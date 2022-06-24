import subprocess
import pathlib
import os

GITHUB_TOKEN = pathlib.Path('GITHUB_TOKEN').read_text()
CONF = pathlib.Path('conf.py')

subprocess.call('jupyter-book config sphinx .', shell=True)

env = os.environ.copy()
env['SPHINX_GITHUB_CHANGELOG_TOKEN '] = GITHUB_TOKEN

_conf = CONF.read_text().split('\n')
_conf = _conf + ['import os'] + ['sphinx_github_changelog_token = os.environ.get("SPHINX_GITHUB_CHANGELOG_TOKEN")']
CONF.write_text("\n".join(_conf))
subprocess.call('sphinx-build . _build/html -b html', shell=True, env=env)
