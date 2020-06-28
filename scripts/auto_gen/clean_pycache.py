def clean_pycache(dir_, ignores=''):
    import shutil

    for path in dir_.glob('**/__pycache__'):
        if ignores and path.match(ignores):
            continue

        shutil.rmtree(path)


if __name__ == "__main__":
    from pathlib import Path

    clean_pycache(Path(__file__).parents[2])
