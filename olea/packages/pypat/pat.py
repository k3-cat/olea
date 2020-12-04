__all__ = ['Pat']

import time
from typing import Any, Dict, Tuple

from .cipher import BaseCipher, aes_gcm
from .encoder import base85
from .serializer import BaseCompresser, BaseObjSerializer, json, lzma
from .signer import BaseSigner, hmac


class Serializer():
    def __init__(self, obj_serializer: 'BaseObjSerializer', compresser: 'BaseCompresser'):
        self.s = obj_serializer
        self.c = compresser

    def loads(self, bytes_: bytes) -> Dict[str, Any]:
        return self.s.loads(self.c.decompress(bytes_))

    def dumps(self, obj):
        return self.c.compress(self.s.dumps(obj))


class Cipher():
    def __init__(self, key: bytes, alg: 'BaseCipher'):
        self.k = alg.Key(key)
        self.c = alg

    @property
    def is_aead(self) -> bool:
        return self.c.is_aead

    def encrypt(self, data: bytes) -> Tuple[bytes, bytes]:
        return self.c.encrypt(self.k, data)

    def decrypt(self, nonce: bytes, data: bytes) -> bytes:
        return self.c.decrypt(self.k, nonce, data)


class Signer():
    def __init__(self, key: bytes, alg: 'BaseSigner'):
        self.k = alg.Key(key)
        self.s = alg

    def sign(self, data: bytes) -> bytes:
        return self.s.sign(self.k, data)

    def verify(self, data: bytes, sig: bytes) -> None:
        return self.s.verify(self.k, data, sig)


class Pat():
    def __init__(self,
                 obj_serializer=json,
                 compresser=lzma,
                 encoder=base85,
                 signer=hmac,
                 sign_key=b'',
                 cipher=aes_gcm,
                 cipher_key=b''):

        self.serializer = Serializer(obj_serializer, compresser)
        self.signer = Signer(key=sign_key, alg=signer)
        self.cipher = Cipher(key=cipher_key, alg=cipher)
        self.encoder = encoder

    def encode(self, exp: int, payload, head: dict = {}) -> str:
        # _b : bytes
        # _*c : encrypted
        nonce, payload_bc = self.cipher.encrypt(self.serializer.dumps(payload))

        head['exp'] = int(time.time()) + exp
        head['nonce'] = self.encoder.encode(nonce)
        head_b = self.serializer.dumps(head)

        sig = self.signer.sign(head_b if self.cipher.is_aead else head_b + payload_bc)

        return (f'{self.encoder.encode(head_b)}:{self.encoder.encode(payload_bc)}:'
                f'{self.encoder.encode(sig)}')

    def decode(self, token: str, ignore_exp=False):
        head, payload = self.decode_with_head(token)
        return payload

    def decode_with_head(self, token: str, ignore_exp=False):
        # _b : bytes
        # _*c : encrypted
        # _*e : encoded
        head_be, payload_bce, sig_e = token.split(':')
        head_b = self.encoder.decode(head_be)
        payload_bc = self.encoder.decode(payload_bce)
        sig = self.encoder.decode(sig_e)

        self.signer.verify(data=head_b if self.cipher.is_aead else head_b + payload_bc, sig=sig)

        head = self.serializer.loads(head_b)
        if head['exp'] < int(time.time()) and not ignore_exp:
            raise Exception()

        payload = self.serializer.loads(
            self.cipher.decrypt(nonce=self.encoder.decode(head['nonce']), data=payload_bc))

        return (head, payload)
