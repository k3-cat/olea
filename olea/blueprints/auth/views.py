from flask import g, jsonify

from olea.auth import login, perm

from . import bp
from .forms import AlterDuck, AlterScopes, ForgetPwd, Login, Refresh, ResetPwd, SetPwd
from .services import DuckMgr, LemonMgr, PinkMgr


@bp.route('/login', methods=['POST'])
def login():
    form = Login()
    lemon = LemonMgr.grante(name=form.name, pwd=form.pwd, device_id=form.device_id)
    return jsonify({'id': lemon.id, 'key': lemon.key, 'exp': lemon.exp})


@bp.route('/set-pwd', methods=['POST'])
@login
def set_pwd():
    form = SetPwd()
    PinkMgr(g.pink_id).set_pwd(form.pwd)
    return jsonify({})


@bp.route('/forget-pwd', methods=['POST'])
def reset_pwd_i():
    form = ForgetPwd()
    PinkMgr.forget_pwd(name=form.name, email=form.email)
    return jsonify({})


@bp.route('/reset-pwd', methods=['POST'])
def reset_pwd():
    form = ResetPwd()
    PinkMgr.reset_pwd(token=form.token, pwd=form.pwd)
    return jsonify({})


@bp.route('/refresh', methods=['POST'])
def refresh():
    form = Refresh()
    token, exp = LemonMgr(form.id).grante_access_token(key=form.key, device_id=form.device_id)
    return jsonify({'token': token, 'exp': exp})


@bp.route('/<id_>/revoke-lemon', methods=['POST'])
@login
def revoke_lemon(id_):
    LemonMgr(id_).revoke()
    return jsonify({})


@bp.route('/revoke-all-lemons', methods=['POST'])
@login
def revoke_all_lemons():
    LemonMgr.revoke_all()
    return jsonify({})


@bp.route('/<pink_id>/ducks', methods=['GET'])
@perm(node='auth.duck')
def list_ducks(pink_id):

    return jsonify()


@bp.route('/<id_>/alter-scopes', methods=['POST'])
@perm(node='auth.duck')
def alter_scopes(id_):
    form = AlterScopes()
    duck = DuckMgr(id_)
    if form.method == AlterScopes.Method.diff:
        duck.add_scopes(scopes=form.positive)
        final = duck.remove_scopes(scopes=form.negative)
    else:
        final = duck.alter_scopes(scopes=form.positive)
    return jsonify({'new_scopes': final})


@bp.route('/<pink_id>/alter-ducks', methods=['POST'])
@perm(node='auth.duck')
def alter_ducks(pink_id):
    form = AlterDuck()
    ducks, confilcts = DuckMgr.alter_ducks(pink_id=pink_id, add=form.add, remove=form.remove)
    res = {'ducks': {duck.id: {'node': duck.node, 'scope': duck.scopes} for duck in ducks}}
    if confilcts:
        res['conflicts'] = {
            duck.id: {
                'node': duck.node,
                'scope': duck.scopes
            }
            for duck in confilcts
        }
    return jsonify()
