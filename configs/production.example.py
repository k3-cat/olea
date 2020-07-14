from datetime import timedelta
from pathlib import Path

from .url_mgr import UrlMgr

DIR = Path(__file__).parents[1]


class Config():
    # --- flask -------------------------------------
    DEBUG = False
    MAX_CONTENT_LENGTH = 10 * 1024

    # --- path --------------------------------------
    DATA_FOLDER = DIR / 'data'
    PWDDB_PATH = DATA_FOLDER / 'pwddb'

    # --- dep-graph ---------------------------------------
    RULE = {
        'doc': {
            'ae': {'au', 'ps'},
        },
        'sub': 'doc',
        'ani': 'doc'
    }
    DURATION = {
        'doc': {
            'au': timedelta(days=7),
            'ps': timedelta(days=7),
            'ae': timedelta(days=14),
        },
        'sub': 'doc',
        'ani': 'doc'
    }
    # PROJ_PRE_DUE = timedelta(days=3)
    PIT_SHIFT_BUFFER = timedelta(days=1)

    # --- exp ---------------------------------------
    WEB_EXP = timedelta(minutes=30)

    # --- token life --------------------------------
    TL_ACCESS_TOKEN = timedelta(minutes=10)
    TL_EMAIL_VERIFICATION = timedelta(hours=1)
    TL_NEW_PINK = timedelta(days=3)
    TL_PIT_SUMBIT = timedelta(days=2)
    TL_PWD_RESET = timedelta(minutes=30)
    TL_REFRESH_TOKEN = timedelta(days=90)

    # --- sqlalchemy --------------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_NAME = 'local'
    SQLALCHEMY_DATABASE_URI = UrlMgr.db_url(DB_NAME)

    # --- redis -------------------------------------
    REDIS_NAME = 'local'
    REDIS_URL = UrlMgr.redis_url(REDIS_NAME)

    # --- sentry ------------------------------------
    SENTRY_DSN = '< - secret - >'

    # --- sqlogger ------------------------------------
    SQLOGGER_DIR = DATA_FOLDER / 'logs'
    SQLOGGER_USER_KEY = 'user'

    # --- sendgrid -----------------------------------
    SENDGRID_SENDER = ''
    SENDGRID_API_KEY = '< - secret - >'

    # --- onedrive ----------------------------------
    ONEDRIVE_CLIENT_ID = ''
    ONEDRIVE_CLIENT_SECRET = '< - secret - >'
    ONEDRIVE_DATA_DIR = DATA_FOLDER / 'onedrive'
    ONEDRIVE_ROOT_FOLDER = ''

    # --- ip2loc ------------------------------------
    IP2LOC_IPDB_PATH = DATA_FOLDER / 'ipdb.bin'
    IP2LOC_DOWNLOAD_TOKEN = '< - secret - >'
