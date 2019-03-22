#!/usr/bin/python3

import logging
import os.path
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from sls.main import main  # noqa: E402

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('lsp.log'),
        logging.StreamHandler()
    ])

if __name__ == '__main__':
    main()
