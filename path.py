__all__ = ['DATA_DIR', 'DIR', 'OLEA_DIR', 'register_olea', 'register_packages']

import sys
from pathlib import Path

from olea.olea_path import DATA_DIR, OLEA_DIR, register_packages

DIR = Path(__file__).parent


def register_olea():
    sys.path.append(str(OLEA_DIR))
    register_packages()
