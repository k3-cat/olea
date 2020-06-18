from pathlib import Path

DIR = Path(__file__).parents[2]

for path in DIR.glob('**/__pycache__'):
    path.unlink()
