from .lemon_auth import LemonAuth

lemon_auth = LemonAuth(scheme='OLEA')

login_required = lemon_auth.login_required
