from .duck_permission import DuckPermission
from .lemon_auth import LemonAuth

lemon_auth = LemonAuth(scheme='OLEA')
duck_permission = DuckPermission(login=lemon_auth.login_required)

login = lemon_auth.login_required
perm = duck_permission.permission_required
