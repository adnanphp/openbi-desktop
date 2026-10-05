"""Allow `python -m openbi_desktop` to launch the app."""

import sys

from openbi_desktop.main import main

if __name__ == "__main__":
    sys.exit(main())
