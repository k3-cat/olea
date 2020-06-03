import base64 as base64
from abc import ABC, abstractstaticmethod

__all__ = ['BaseEncoder', 'base64', 'base85']


class BaseEncoder(ABC):
    @abstractstaticmethod
    def encode(bytes_: bytes) -> str:
        return ''

    @abstractstaticmethod
    def decode(string: str) -> bytes:
        return b''


class base64(BaseEncoder):
    @staticmethod
    def encode(bytes_: bytes):
        return base64.encodebytes(bytes_).decode('utf-8')

    @staticmethod
    def decode(string: str):
        return base64.decodebytes(string.encode('utf-8'))


class base85(BaseEncoder):
    @staticmethod
    def encode(bytes_: bytes):
        return base64.b85encode(bytes_).decode('utf-8')

    @staticmethod
    def decode(string: str):
        return base64.b85decode(string)
