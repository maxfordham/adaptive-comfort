To build, do the following: 

**note: we assume you are in the same dir as this README.txt file. 

1. delete the ../src/__init.py
^ this is here for dev only and makes the doc generator think that ipyautoui is a subpackage of src

2. generate conf.py file from jupyterbook
>>> jupyter-book config sphinx .

3. setting github token for sphinx_github_changelog
- Within conf.py, we use a linux environment variable "GITHUB_TOKEN_CHANGELOG". This must be set before trying to produce the docs using sphinx.
- Note, however, this isn't in the _config.yml file. If we place an environment variable within the _config.yml, producing the conf.py using jupyter-book bugs out.
Issue here: https://github.com/maxfordham/adaptive_comfort/issues/21

Anyway, create the token in Github first. You do this within "Settings" -> "Developer Settings" -> "Personal access tokens".

Copy the code (maybe store it somewhere locally too as you won't be able to access it again through github without regeneration).

Then set the env variable in linux:

```bash
export GITHUB_TOKEN_CHANGELOG=<token>
```

4. generate docs
>>> sphinx-build . _build/html -b html

Notes.
- when authoring notebooks that will be executed the notebook must be authored from directly within the environment - __not__ using nb_conda_kernels

