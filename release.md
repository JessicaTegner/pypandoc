# Making a release

This is the internal checklist, so that @janschulz doesn't have to do another brown paper bag force-pushing the tags...

- checkout `git fetch origin && git checkout origin/master`
- run the tests (on windows): `python tests.py` -> everything ok?
- increment the version in `pypandoc/__init__.py` and `pyproject.toml`, commit with `git commit -m "pypandoc vx.x.x"`
- tag the version: `git tag -a vx.x.x`, write a nice version message summarizing new features
- push directly to the repo: `git push; git push --tags`
- build the sdist and wheel files: `python setup.py sdist bdist_wheel`
- upload to PyPI: `twine upload dist/*`
- go to the [package builder repo](https://github.com/JanSchulz/package-builder) and increment the version information in `recipes\pypandoc\meta.yml`
- commit with `git commit -m "Build pypandoc vx.x.x"`
- `git push` -> builds arrive at [PyPI](https://pypi.python.org/pypi?:action=display&name=pypandoc) and [anaconda](https://anaconda.org/janschulz/pypandoc/files)
- celebrate :-)