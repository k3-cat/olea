__all__ = ['TokenCache']

from msal import SerializableTokenCache


class TokenCache():
    def __init__(self, path):
        self.file_path = path / 'token.json'

        with self.file_path.open('r') as f:
            token = f.read()
        if not token:
            raise Exception('No Token')

        self.cache = SerializableTokenCache()
        self.cache.deserialize(token)

    def save(self):
        if not self.cache.has_state_changed:
            return

        with self.file_path.open('w') as f:
            f.write(self.cache.serialize())
