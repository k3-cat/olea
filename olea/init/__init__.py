import sys
from pathlib import Path

PATH = Path(__file__).parents[2] / 'site-packages'
sys.path.append(str(PATH / 'jsonform'))
sys.path.append(str(PATH / 'pypat'))
sys.path.append(str(PATH))
