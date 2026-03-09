"""Custom hatch hooks for pypandoc_binary.

Metadata hook: reads version, readme, and shared project metadata from the root package.
Build hook: downloads pandoc if needed, includes pypandoc source via
force_include, and ensures the wheel is tagged as platform-specific.

File layout support:
  - Local dev: binary/ is a subdir of the repo root, pypandoc/ is at ../pypandoc/
  - CI / build isolation: pypandoc/, README.md, and root_pyproject.toml are
    pre-copied into binary/ via CIBW_BEFORE_BUILD
"""

import os
import re
import sys
import sysconfig

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.metadata.plugin.interface import MetadataHookInterface

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)


def _find_pypandoc_dir():
    """Find the pypandoc package directory."""
    # Local dev: ../pypandoc relative to binary/
    candidate = os.path.join(_PARENT, "pypandoc")
    if os.path.isfile(os.path.join(candidate, "__init__.py")):
        return candidate
    # CI / build isolation: pypandoc/ copied into binary/
    candidate = os.path.join(_HERE, "pypandoc")
    if os.path.isfile(os.path.join(candidate, "__init__.py")):
        return candidate
    raise FileNotFoundError(
        "Could not find pypandoc package. In CI, ensure CIBW_BEFORE_BUILD "
        "copies pypandoc/ into the package directory."
    )


def _find_readme():
    """Find README.md."""
    for base in [_PARENT, _HERE]:
        path = os.path.join(base, "README.md")
        if os.path.isfile(path):
            return path
    raise FileNotFoundError("Could not find README.md")


def _read_root_pyproject():
    """Parse the root pyproject.toml and return the [project] table.

    In local dev the root pyproject.toml lives one directory up (_PARENT).
    In CI / build isolation it is pre-copied as root_pyproject.toml into _HERE
    (to avoid overwriting the binary package's own pyproject.toml).
    """
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    candidates = [
        os.path.join(_PARENT, "pyproject.toml"),
        os.path.join(_HERE, "root_pyproject.toml"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "rb") as f:
                return tomllib.load(f)["project"]
    raise FileNotFoundError("Could not find root pyproject.toml")


class CustomMetadataHook(MetadataHookInterface):
    def update(self, metadata):
        pypandoc_dir = _find_pypandoc_dir()

        # Read version from pypandoc/__init__.py
        init_path = os.path.join(pypandoc_dir, "__init__.py")
        with open(init_path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'^__version__\s*=\s*["\']([^"\']+)["\']', line)
                if m:
                    metadata["version"] = m.group(1)
                    break

        # Read readme
        readme_path = _find_readme()
        with open(readme_path, encoding="utf-8") as f:
            metadata["readme"] = {
                "content-type": "text/markdown",
                "text": f.read(),
            }

        # Read shared metadata from root pyproject.toml
        root = _read_root_pyproject()
        for key in (
            "description",
            "license",
            "requires-python",
            "authors",
            "classifiers",
        ):
            if key in root:
                metadata[key] = root[key]
        if "urls" in root:
            metadata["urls"] = root["urls"]


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        pypandoc_dir = _find_pypandoc_dir()
        files_dir = os.path.join(pypandoc_dir, "files")

        # Check if pandoc binary already exists (CI pre-downloads it)
        pandoc_exists = os.path.isfile(
            os.path.join(files_dir, "pandoc")
        ) or os.path.isfile(os.path.join(files_dir, "pandoc.exe"))

        if not pandoc_exists:
            # Ensure pypandoc is importable
            parent = os.path.dirname(pypandoc_dir)
            if parent not in sys.path:
                sys.path.insert(0, parent)
            from pypandoc.pandoc_download import download_pandoc

            download_pandoc(targetfolder=files_dir)

        # Include the pypandoc package in the wheel
        build_data["force_include"][pypandoc_dir] = "pypandoc"

        # Tag as py3-none-<platform> — no compiled extensions, just a
        # bundled pandoc binary.  cibuildwheel's auditwheel/delocate will
        # repair the platform tag to manylinux/musllinux as needed.
        plat = sysconfig.get_platform().replace("-", "_").replace(".", "_")
        build_data["tag"] = f"py3-none-{plat}"
