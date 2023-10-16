"""Main script package for PoRTo.

Append current folder to os.path: ensure that future imports of subpackages
do not fail.
"""

import os, sys


sys.path.append(os.path.dirname(__file__))
#