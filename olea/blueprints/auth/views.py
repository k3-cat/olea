from flask import jsonify

from olea.auth import login, perm

from . import bp
from .forms import AlterScopes, GrantedDuck, Login, Refresh
from .services import DuckMgr, LemonMgr


@bp.route('/login', methods=['POST'])
def login():
    form = Login()
    lemon = LemonMgr.create(name=form.name, pwd=form.pwd, device_id=form.device_id)
    return jsonify({'lemon': lemon.id, 'key': lemon.key})


@bp.route('/refresh', methods=['POST'])
def refresh():
    form = Refresh()
    token, exp = LemonMgr(form.id).granted_access_token(key=form.key, device_id=form.device_id)
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


@bp.route('/granted-duck', methods=['POST'])
@perm(node='auth.duck')
def granted_duck():
    form = GrantedDuck()
    duck = DuckMgr.create(pink_id=form.pink_id, node=form.node, scopes=form.scopes)
    return jsonify({'id': duck.id})


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


@bp.route('/<id_>/revoke-duck', methods=['POST'])
@perm(node='auth.duck')
def revoke_d(id_):
    DuckMgr(id_).revoke()
    return jsonify({})
