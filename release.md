# Making a release

This is the internal checklist, so that @janschulz doesn't have to do another brown paper bag force-pushing the tags...

- checkout `git fetch origin && git checkout origin/master`
- run the tests: `python tests.py` -> everything ok?
- increment the version in `pypandoc/__init__.py`, commit with `git commit -m "pypandoc x.x.x"`
- tag the version: `git tag -a x.x.x`, write a nice version message summarizing new features
- push directly to the repo (registered as `orig_write` in my setup): `git push orig_write HEAD:master --tags`
- celebrate :-)
