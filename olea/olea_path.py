import sys
from pathlib import Path

OLEA_DIR = Path(__file__).parent

CONFIGS_DIR = OLEA_DIR / 'configs'
CORE_DIR = OLEA_DIR / 'core'
DATA_DIR = OLEA_DIR / 'data'
MODELS_DIR = OLEA_DIR / 'models'
PACKAGES_DIR = OLEA_DIR / 'packages'


def register_packages():
    sys.path.append(str(PACKAGES_DIR / 'json_api'))
    sys.path.append(str(PACKAGES_DIR))
