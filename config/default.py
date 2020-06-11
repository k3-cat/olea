import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parents[1] / 'data'

DEBUG = False

SQLALCHEMY_TRACK_MODIFICATIONS = False

MAX_CONTENT_LENGTH = 10 * 1024

WEB_EXP = 60 * 3
IP_RECORD_EXP = 86400 * 60

ACCESS_TOKEN_LIFE = datetime.timedelta(minutes=10)
REFRESH_TOKEN_LIFE = datetime.timedelta(days=90)
RESET_PWD_TOKEN_LIFE = datetime.timedelta(minutes=30)

ARGON2_TIME_COST = 0
ARGON2_MEMORY_COST = 0
ARGON2_PARALLELISM = 0

ONEDRIVE_CLIENT_ID = '64d4612f-710b-415e-bbb5-f3e38294d744'
ONEDRIVE_TOKEN_PATH = DATA_DIR / 'token'
ONEDRIVE_ROOT_FOLDER = 'root:/olea-storage:'

MAILGUN_DOMAIN = 'mail.cybil.xyz'
MAILGUN_SENDER = 'olea'

IPDB_PATH = DATA_DIR / 'ipdb.bin'
PWDDB_PATH = DATA_DIR / 'pwddb'
