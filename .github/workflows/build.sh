#!/bin/bash
set -e -u -x

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install -U pip wheel setuptools twine
    "${PYBIN}/python" /io/setup_binary.py download_pandoc bdist_wheel
    "${PYBIN}/python" /io/setup.py sdist bdist_wheel
done
