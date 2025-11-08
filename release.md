# Making a release

This is the internal checklist, so that @janschulz doesn't have to do another brown paper bag force-pushing the tags...

- checkout `git fetch origin && git checkout origin/master`
- run the tests (on windows): `python tests.py` -> everything ok?
- increment the version in `pypandoc/__init__.py` and `pyproject.toml`, commit with `git commit -m "pypandoc vx.x.x"`
- tag the version: `git tag -a vx.x.x`, write a nice version message summarizing new features
- push directly to the repo: `git push; git push --tags`
- celebrate :-)

