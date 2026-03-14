"""Command-line interface for pypandoc."""

from __future__ import annotations

import argparse
import sys

from .handler import _check_log_handler


def main(argv=None):
    """Entry point for ``python -m pypandoc`` and the ``pypandoc`` console script."""
    _check_log_handler()

    parser = argparse.ArgumentParser(
        prog="pypandoc",
        description="Thin wrapper for pandoc.",
    )
    sub = parser.add_subparsers(dest="command")

    # version
    sub.add_parser("version", help="Show pypandoc and pandoc versions")

    # pandoc
    p_pandoc = sub.add_parser(
        "pandoc",
        help="Pass arguments through to the pandoc binary",
        add_help=False,
    )
    p_pandoc.add_argument("pandoc_args", nargs=argparse.REMAINDER)

    # download
    p_download = sub.add_parser("download", help="Download pandoc")
    p_download.add_argument("--url", default=None, help="URL to download pandoc from")
    p_download.add_argument(
        "--target", default=None, help="Target folder for the pandoc installation"
    )
    p_download.add_argument(
        "--version",
        default="latest",
        help="Pandoc version to download (default: latest)",
    )
    p_download.add_argument(
        "--delete-installer",
        action="store_true",
        help="Delete the installer after extraction",
    )
    p_download.add_argument(
        "--download-folder",
        default=None,
        help="Folder to download the installer to before extraction",
    )

    # If the subcommand is "pandoc", pass everything after it verbatim
    # so argparse doesn't intercept flags like --version or --help.
    raw = argv if argv is not None else sys.argv[1:]
    if raw and raw[0] == "pandoc":
        args = argparse.Namespace(command="pandoc", pandoc_args=raw[1:])
    else:
        args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    import pypandoc

    try:
        if args.command == "version":
            print("pypandoc %s" % pypandoc.__version__)
            try:
                print("pandoc info:")
                pandoc_path = pypandoc.get_pandoc_path()
                import subprocess

                subprocess.call([pandoc_path, "--version"])
            except OSError:
                print("pandoc not found")
            try:
                import pytinytex

                print("pytinytex %s" % pytinytex.__version__)
            except ImportError:
                print("pytinytex not installed")

        elif args.command == "pandoc":
            import subprocess

            try:
                pandoc_path = pypandoc.get_pandoc_path()
            except OSError:
                print(
                    "Error: pandoc not found. Install pandoc or run "
                    "'pypandoc download' to download it.",
                    file=sys.stderr,
                )
                return 1
            sys.exit(subprocess.call([pandoc_path] + args.pandoc_args))

        elif args.command == "download":
            pypandoc.download_pandoc(
                url=args.url,
                targetfolder=args.target,
                version=args.version,
                delete_installer=args.delete_installer,
                download_folder=args.download_folder,
            )
            print("Done.")

    except RuntimeError as e:
        print("Error: %s" % e, file=sys.stderr)
        return 1

    return 0
