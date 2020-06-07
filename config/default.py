import datetime
from pathlib import Path

DEBUG = False

SQLALCHEMY_TRACK_MODIFICATIONS = False

MAX_CONTENT_LENGTH = 10 * 1024

ACCESS_TOKEN_LIFE = datetime.timedelta(minutes=10)
REFRESH_TOKEN_LIFE = datetime.timedelta(days=90)

ONEDRIVE_CLIENT_ID = ''
ONEDRIVE_TOKEN_FILE_PATH = Path(__file__).parent / 'token'
ONEDRIVE_ROOT_FOLDER = 'root:/olea-storage:'

MAILGUN_DOMAIN = 'mail.cybil.xyz'
MAILGUN_SENDER = 'olea'

IPDB_PATH = Path(__file__).parent / 'ipdb.bin'
