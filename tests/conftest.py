﻿# Ensures "import x987" works without installing a package.
import sys, pathlib
root = pathlib.Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
