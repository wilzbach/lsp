#!/usr/bin/python3
# Convenience CLI wrapper for the Storyscript Language Server

import os.path
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from sls.cli import Cli  # noqa: E402

if __name__ == '__main__':
    Cli.main()
