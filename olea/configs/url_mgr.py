import os
from pathlib import Path

import toml


class UrlMgr():
    urls = toml.load(Path(__file__).parent / 'urls.toml')

    @staticmethod
    def redis_url(name):
        return UrlMgr.get_url('redis', name)

    @staticmethod
    def db_url(name):
        return UrlMgr.get_url('db', name)

    @classmethod
    def get_url(cls, cat: str, name: str = ''):
        name = os.getenv(f'{cat.upper()}_NAME', name)
        return cls.urls[cat.lower()][name]
