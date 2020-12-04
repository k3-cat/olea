__all__ = ['BaseObjSerializer', 'json', 'pickle', 'BaseCompresser', 'lzma']

import json as _json
import lzma as _lzma
import pickle as _pickle


class BaseObjSerializer():
    @staticmethod
    def loads(byte_: bytes):
        return dict()

    @staticmethod
    def dumps(obj) -> bytes:
        return b''


class json(BaseObjSerializer):
    @staticmethod
    def loads(bytes_):
        return _json.loads(bytes_.decode('utf-8'))

    @staticmethod
    def dumps(obj):
        return _json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


class pickle(BaseObjSerializer):
    @staticmethod
    def loads(bytes_):
        return _pickle.loads(bytes_)

    @staticmethod
    def dumps(obj):
        return _pickle.dumps(obj, protocol=_pickle.HIGHEST_PROTOCOL)


class BaseCompresser():
    @staticmethod
    def compress(data: bytes) -> bytes:
        raise NotImplementedError()

    @staticmethod
    def decompress(data: bytes) -> bytes:
        raise NotImplementedError


class lzma(BaseObjSerializer):
    _format_ = _lzma.FORMAT_RAW
    _filters_ = [{'id': _lzma.FILTER_LZMA2, 'preset': 6}]

    @staticmethod
    def compress(data):
        return _lzma.compress(data, lzma._format_, filters=lzma._filters_)

    @staticmethod
    def decompress(data):
        return _lzma.decompress(data, lzma._format_, filters=lzma._filters_)
