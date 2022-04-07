if [ $TRAVIS_OS_NAME = 'osx' ]; then
    python3 -m pip install poetry
else
    python -m pip install poetry
fi
