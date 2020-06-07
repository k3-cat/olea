from flask import jsonify

from olea.auth import login_required

from . import bp
from .forms import Login, Refresh
from .services import AuthMgr


@bp.route('/login', methods=['POST'])
def login():
    form = Login()
    lemon = AuthMgr.create(name=form.name, pwd=form.pwd, device_id=form.device_id)
    return jsonify({'lemon': lemon.id, 'key': lemon.key})


@bp.route('/refresh', methods=['POST'])
def refresh():
    form = Refresh()
    token, exp = AuthMgr(form.id).granted_access_token(key=form.key)
    return jsonify({'token': token, 'exp': exp})


@bp.route('/<id_>/revork', methods=['POST'])
@login_required
def revork(id_):
    AuthMgr(id_).revoke()
    return jsonify({})


@bp.route('/revork_all', methods=['POST'])
@login_required
def revork_all():
    AuthMgr.revoke_all()
    return jsonify({})
