import os
import sys
from pathlib import Path

def add_parent():
    path = Path(os.path.realpath(__file__)).parent.parent
    sys.path.append(str(path))
