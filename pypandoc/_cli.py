"""CLI entry point that forwards to the bundled pandoc binary."""

import os
import subprocess
import sys


def main():
    # Locate the bundled pandoc binary
    files_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")
    pandoc = os.path.join(
        files_dir, "pandoc.exe" if sys.platform == "win32" else "pandoc"
    )

    if not os.path.isfile(pandoc):
        print("pypandoc_binary: bundled pandoc not found at", pandoc, file=sys.stderr)
        sys.exit(1)

    # Add files dir to PATH for pandoc-citeproc discovery
    env = os.environ.copy()
    env["PATH"] = files_dir + os.pathsep + env.get("PATH", "")

    sys.exit(
        subprocess.call(
            [pandoc] + sys.argv[1:],
            env=env,
        )
    )


if __name__ == "__main__":
    main()
