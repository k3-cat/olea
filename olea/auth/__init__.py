from .duck_permission import DuckPermission
from .lemon_auth import LemonAuth

lemon_auth = LemonAuth(scheme='OLEA')
duck_permission = DuckPermission()

login_req = lemon_auth.login_required
permission_req = duck_permission.permission_required
