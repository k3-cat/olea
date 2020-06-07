import IP2Location
from flask import current_app

ip2loc = IP2Location.IP2Location(current_app.config['IPDB_PATH'], 'SHARED_MEMORY')
