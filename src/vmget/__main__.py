"""Entry point for running vmget as a module: python -m vmget"""

import sys
from vmget.cli import main

if __name__ == "__main__":
    sys.exit(main())
