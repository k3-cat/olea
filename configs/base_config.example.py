from datetime import timedelta
from pathlib import Path

from .url_mgr import UrlMgr

PROJ_ROOT = Path(__file__).parents[1]


class Config():
    # --- flask -------------------------------------
    DEBUG = False
    MAX_CONTENT_LENGTH = 10 * 1024

    # --- path --------------------------------------
    DATA_FOLDER = PROJ_ROOT / 'data'
    IPDB_PATH = DATA_FOLDER / 'ipdb.bin'
    PWDDB_PATH = DATA_FOLDER / 'pwddb'

    # --- exp ---------------------------------------
    WEB_EXP = timedelta(minutes=30)
    IP_RECORD_EXP = timedelta(days=60)

    # --- token life --------------------------------
    ACCESS_TOKEN_LIFE = timedelta(minutes=10)
    REFRESH_TOKEN_LIFE = timedelta(days=90)
    RESET_PWD_TOKEN_LIFE = timedelta(minutes=30)

    # --- argon2 ------------------------------------
    ARGON2_TIME_COST = 0
    ARGON2_MEMORY_COST = 0
    ARGON2_PARALLELISM = 0

    # --- sqlalchemy --------------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_NAME = 'local'
    SQLALCHEMY_DATABASE_URI = UrlMgr.db_url(DB_NAME)

    # --- alembic -----------------------------------
    ALEMBIC = {
        'script_location': PROJ_ROOT / 'migrations',
        'file_template': '%%(rev)s',
        'timezone': 'UTC'
    }
    ALEMBIC_CONTEXT = {'url': SQLALCHEMY_DATABASE_URI}

    # --- redis -------------------------------------
    REDIS_NAME = 'local'
    REDIS_URL = UrlMgr.redis_url(REDIS_NAME)

    # --- sentry ------------------------------------
    SENTRY_DSN = '< - secret - >'

    # --- mailgun -----------------------------------
    MAILGUN_DOMAIN = ''
    MAILGUN_SENDER = ''
    MAILGUN_API_KEY = '< - secret - >'

    # --- onedrive ----------------------------------
    ONEDRIVE_CLIENT_ID = ''
    ONEDRIVE_CLIENT_SECRET = '< - secret - >'
    ONEDRIVE_TOKEN_PATH = DATA_FOLDER / 'token'
    ONEDRIVE_ROOT_FOLDER = ''

    # --- ip2loc ------------------------------------
    IP2LOC_API_KEY = '< - secret - >'
    IP2LOC_DOWNLOAD_TOKEN = '< - secret - >'
