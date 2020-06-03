import json as json_
import lzma as lzma_
import pickle as pickle_
from abc import ABC, abstractstaticmethod

__all__ = ['BaseObjSerilizer', 'json', 'pickle' 'BaseCompresser', 'lzma']


class BaseObjSerilizer(ABC):
    @abstractstaticmethod
    def loads(byte_: bytes):
        return object()

    @abstractstaticmethod
    def dumps(obj) -> bytes:
        return b''


class json(BaseObjSerilizer):
    @staticmethod
    def loads(bytes_):
        return json_.loads(bytes_.decode('utf-8'))

    @staticmethod
    def dumps(obj):
        return json_.dumps(obj, ensure_ascii=False,
                           separators=(',', ':')).encode('utf-8')


class pickle(BaseObjSerilizer):
    @staticmethod
    def loads(bytes_):
        return pickle_.loads(bytes_)

    @staticmethod
    def dumps(obj):
        return pickle_.dumps(obj, protocol=pickle_.HIGHEST_PROTOCOL)


class BaseCompresser(ABC):
    @abstractstaticmethod
    def compress(data: bytes) -> bytes:
        raise NotImplementedError()

    @abstractstaticmethod
    def decompress(data: bytes) -> bytes:
        raise NotImplementedError


class lzma(BaseObjSerilizer):
    _format_ = lzma_.FORMAT_RAW
    _filters_ = [{'id': lzma_.FILTER_LZMA2, 'preset': 6}]

    @staticmethod
    def compress(data):
        return lzma_.compress(data, lzma._format_, filters=lzma._filters_)

    @staticmethod
    def decompress(data):
        return lzma_.decompress(data, lzma._format_, filters=lzma._filters_)
