import json
from hashlib import sha3_256
from pathlib import Path

from path import OLEA_DIR, DATA_DIR


class Version():
    def __init__(self):
        self.temp = dict()
        self.file_path = DATA_DIR / 'version.json'

        try:
            with self.file_path.open('r') as f:
                self.ver = json.load(f)

        except FileNotFoundError:
            self.ver = dict()

    def clean_path(self, path: Path, root=None):
        if root:
            return str(path.relative_to(root)).replace('\\', '/')

        return str(path.relative_to(OLEA_DIR)).replace('\\', '/')

    def check_dir(self, path: str, ignores: list):
        ver = self.ver.get(path, dict())
        temp = dict()
        changed = list()

        module_dir = OLEA_DIR / path
        for p in module_dir.iterdir():
            key = self.clean_path(p, module_dir)
            if key in ignores:
                continue

            with p.open('rb') as f:
                sha3 = sha3_256(f.read()).hexdigest()
            if sha3 == ver.get(key, None):
                continue

            changed.append(p)
            temp[key] = sha3

        if temp:
            self.temp[path] = temp

        return changed

    def save(self, path):
        if path not in self.temp:
            return

        self.ver.setdefault(path, dict())
        self.ver[path].update(self.temp[path])

        with self.file_path.open('w') as f:
            json.dump(self.ver, f, indent=2)
