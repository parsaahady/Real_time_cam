"""Entry point: python main.py --host <receiver-ip>."""

import sys

from camlab.cli import main

if __name__ == "__main__":
    sys.exit(main())