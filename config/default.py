import datetime

DEBUG = False

SQLALCHEMY_TRACK_MODIFICATIONS = False

MAX_CONTENT_LENGTH = 10 * 1024
TOKEN_LIFE = datetime.timedelta(days=90)

MAILGUN_DOMAIN = 'mail.cybil.xyz'
MAILGUN_SENDER = 'olea'
