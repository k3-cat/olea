from pathlib import Path

DIR = Path(__file__).parents[2]

ignores = DIR / '.gitignore'

for path in DIR.glob('*'):
    pass
