__all__ = ['Index']

import json

_alphabet = '0123456789aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ-_()!'


class Index():
    folder_map = {char: _alphabet[_alphabet.index(char) // 2 * 2] for char in _alphabet}

    def __init__(self, config, api):
        self.file_path = config['data_dir'] / 'index.json'

        try:
            with self.file_path.open('r') as f:
                self.index = json.load(f)

        except FileNotFoundError:
            self.index = dict()
            children = api.get(f'/me/drive/{config["root_folder"]}/children')['value']
            self.index['drive_id'] = children[0]['parentReference']['driveId']

            for child in children:
                if 'folder' not in child:
                    continue

                self.index[child['name']] = child['id']

            with self.file_path.open('w') as f:
                json.dump(self.index, f, indent=2)

    def get_folder(self, name):
        return self.folder_map[name[0]]

    def get_folder_ref(self, name):
        return {
            'driveId': self.index['drive_id'],
            'id': self.index[self.get_folder(name)],
        }
