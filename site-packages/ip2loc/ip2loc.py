__all__ = ['IP2Loc']

import IP2Location

from .update_ipdb import download


class IP2Loc():
    def __init__(self, app=None):
        self.ip2loc = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        path = app.config['IP2LOC_IPDB_PATH']
        if not path.exists():
            download(path, app.config['IP2LOC_DOWNLOAD_TOKEN'])
        self.ip2loc = IP2Location.IP2Location(path, 'SHARED_MEMORY')

    def get_city(self, ip):
        return self.ip2loc.get_city(ip)
