import os
import sys

from runner_helper import run

if __name__ == "__main__":
    r = run()
    sys.exit(os.EX_SOFTWARE if r > 0 else os.EX_OK)
