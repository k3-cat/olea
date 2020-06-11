import datetime

import IP2Location
import requests
from flask import current_app

from olea.exts import redis

EX = current_app.config['IP_RECORD_EXP']
API_KEY = current_app.config['IP2LOC_API_KEY']
ip2loc = IP2Location.IP2Location(current_app.config['IPDB_PATH'], 'SHARED_MEMORY')


def ip2city(ip):
    if city := redis.get(f'ip2city-{ip}'):
        return city

    if not redis.get('ip-lock'):
        res = requests.get(f'https://api.ip2location.com/v2/?ip={ip}&key={API_KEY}&package=WS3')
        data = res.json()
        if 'response' not in data:
            city = data['city_name']
            redis.set(f'ip2city-{ip}', city, ex=EX)
            return city
        now = datetime.datetime.utcnow()
        sec = 86400 - now.hour * 3600 - now.minute * 60 - now.second
        redis.set('ip-lock', now.timestamp(), ex=sec)

    return ip2loc.get_city(ip)
