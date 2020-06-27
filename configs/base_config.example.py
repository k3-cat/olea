from datetime import timedelta
from pathlib import Path

from models import Dep

from .url_mgr import UrlMgr

DIR = Path(__file__).parents[1]


class Config():
    # --- flask -------------------------------------
    DEBUG = False
    MAX_CONTENT_LENGTH = 10 * 1024

    # --- path --------------------------------------
    DATA_FOLDER = DIR / 'data'
    IPDB_PATH = DATA_FOLDER / 'ipdb.bin'
    PWDDB_PATH = DATA_FOLDER / 'pwddb'

    # --- dep-graph ---------------------------------------
    RULE = {
        Dep.ae: {Dep.au, Dep.ps},
    }
    DURATION = {
        Dep.au: timedelta(days=7),
        Dep.ps: timedelta(days=7),
        Dep.ae: timedelta(days=14),
    }
    # PROJ_PRE_DUE = timedelta(days=3)
    PIT_SHIFT_BUFFER = timedelta(days=1)

    # --- exp ---------------------------------------
    WEB_EXP = timedelta(minutes=30)

    # --- token life --------------------------------
    DEPS_TOKEN_LIFE = timedelta(days=3)
    EMAIL_VERIFICATION_LIFE = timedelta(hours=1)
    ACCESS_TOKEN_LIFE = timedelta(minutes=10)
    REFRESH_TOKEN_LIFE = timedelta(days=90)
    PWD_RESET_TOKEN_LIFE = timedelta(minutes=30)

    # --- sqlalchemy --------------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_NAME = 'local'
    SQLALCHEMY_DATABASE_URI = UrlMgr.db_url(DB_NAME)

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
    ONEDRIVE_DATA_DIR = DATA_FOLDER / 'onedrive'
    ONEDRIVE_ROOT_FOLDER = ''

    # --- ip2loc ------------------------------------
    IP2LOC_DOWNLOAD_TOKEN = '< - secret - >'
