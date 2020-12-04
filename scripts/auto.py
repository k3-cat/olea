import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))

if __name__ == "__main__":
    from alan import main

    main()
