"""Allow running pypandoc as ``python -m pypandoc``."""

import sys

from .cli import main

sys.exit(main())
