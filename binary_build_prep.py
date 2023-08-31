import os
from pypandoc.pandoc_download import download_pandoc

import subprocess
import sys

check_result = subprocess.call(["patch", "--dry-run", "-N", "-u", "pyproject.toml", "-i", "pyproject.toml.patch"])
if check_result != 0:
    print("Something is wrong with the pyproject.toml patch")
    sys.exit(1)


patch_result = subprocess.check_call(["patch", "-u", "pyproject.toml", "-i", "pyproject.toml.patch"])
if patch_result != 0:
    print("Something went wrong when patching pyproject.toml")
    sys.exit(2)


print("Downloading pandoc")
targetfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pypandoc", "files")
download_pandoc(targetfolder=targetfolder)

