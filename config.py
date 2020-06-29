import multiprocessing
import os

import gevent.monkey

gevent.monkey.patch_all()


# debug = True
loglevel = 'info'
bind = 'unix:/tmp/olea.sock'
pidfile = '/run/olea.pid'
accesslog = '/var/log/olea/access.log'
errorlog = '/var/log/olea/error.log'
daemon = True

workers = multiprocessing.cpu_count() * 2 - 1
worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'
