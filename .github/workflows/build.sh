#!/bin/bash
set -e -u -x

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install -U pip wheel setuptools twine
    "${PYBIN}/python" setup_binary.py download_pandoc bdist_wheel
    "${PYBIN}/python" setup.py sdist bdist_wheel
done
