"""Main script package for PoRTo.

Append current folder to os.path and ensure that future imports of subpackage
do not fail."""

import os, sys


sys.path.append(os.path.dirname(__file__))