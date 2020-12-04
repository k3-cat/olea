__all__ = ['BaseSigner', 'hmac', 'ed25519', 'ed25519_v']

import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.hmac import HMAC, hashes


class BaseSigner():
    class Key():
        def __init__(self, key: bytes):
            pass

        def export(self) -> bytes:
            return b''

    @staticmethod
    def sign(key: 'BaseSigner.Key', data: bytes) -> bytes:
        return b''

    @staticmethod
    def verify(key: 'BaseSigner.Key', data: bytes, sig: bytes) -> None:
        pass


class hmac(BaseSigner):
    class Key(BaseSigner.Key):
        def __init__(self, key: bytes):
            self.key = key if key else os.urandom(256 // 8)

        def export(self) -> bytes:
            return self.key

    @staticmethod
    def sign(key: 'hmac.Key', data):
        h = HMAC(key.key, hashes.SHA3_256(), default_backend())
        h.update(data)
        return h.finalize()

    @staticmethod
    def verify(key: 'hmac.Key', data, sig):
        h = HMAC(key.key, hashes.SHA3_256(), default_backend())
        h.update(data)
        h.verify(sig)


class ed25519(BaseSigner):
    class Key(BaseSigner.Key):
        def __init__(self, key: bytes):
            if not key:
                private = Ed25519PrivateKey.generate()
            else:
                private = Ed25519PrivateKey.from_private_bytes(key)
            self.private = private
            self.public: Ed25519PublicKey = self.private.public_key()

        def export(self, private=False) -> bytes:
            if private:
                return self.private.private_bytes(encoding=serialization.Encoding.Raw,
                                                  format=serialization.PrivateFormat.Raw,
                                                  encryption_algorithm=serialization.NoEncryption())
            return self.public.public_bytes(encoding=serialization.Encoding.Raw,
                                            format=serialization.PublicFormat.Raw)

    @staticmethod
    def sign(key: 'ed25519.Key', data):
        return key.private.sign(data)

    @staticmethod
    def verify(key: 'ed25519.Key', data, sig):
        key.public.verify(sig, data)


class ed25519_v(BaseSigner):
    class Key(BaseSigner.Key):
        def __init__(self, key: bytes):
            if not key:
                raise Exception()
            self.public = Ed25519PublicKey.from_public_bytes(key)

        def export(self) -> bytes:
            return self.public.public_bytes(encoding=serialization.Encoding.Raw,
                                            format=serialization.PublicFormat.Raw)

    @staticmethod
    def sign(key, data):
        raise NotImplementedError()

    @staticmethod
    def verify(key: 'ed25519_v.Key', data, sig):
        key.public.verify(sig, data)
