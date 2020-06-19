from flask import g, jsonify, request

from olea.auth import allow_anonymous, opt_perm, perm

from . import bp
from .forms import AlterDuck, AlterScopes, AssignToken, SignUp, Search, SearchDuck, UpdateInfo
from .services import DuckMgr, PinkMgr
from .query import PinkQuery


@bp.route('/<id_>', methods=['GET'])
@opt_perm
def single(id_):
    pink = PinkQuery.single(id_)
    return jsonify({})


@bp.route('/', methods=['GET'])
@opt_perm
def search():
    form = Search(request.args)
    pinks = PinkQuery.search(deps=form.deps, name=form.name, qq=form.qq)
    return pinks


@bp.route('/update-info', methods=['POST'])
def update_info():
    form = UpdateInfo()
    PinkMgr(g.pink_id).update_info(qq=form.qq, other=form.other, email=form.email)
    return 'True'


@bp.route('/assign_token', methods=['POST'])
@perm
def assign_token():
    form = AssignToken()
    token = PinkMgr.assign_token(deps=form.deps, amount=form.amount)
    return jsonify({'token': token})


@bp.route('/sign-up', methods=['POST'])
@allow_anonymous
def sign_up():
    form = SignUp()
    pink = PinkMgr.sign_up(
        name=form.name,
        qq=form.qq,
        other=form.other,
        email_token=form.token_email,
        deps_token=form.token_dep,
    )
    return jsonify({'id': pink.id})


@bp.route('/<id_>/deactive', methods=['POST'])
@perm
def deactive(id_):
    PinkMgr(id_).deactive()
    return jsonify({})


@bp.route('/ducks/', methods=['GET'])
@opt_perm(node='auth.duck')
def list_ducks():
    form = SearchDuck(request.args)
    ducks = PinkQuery.ducks(pink_id=form.pink_id,
                            node=form.node,
                            nodes=form.nodes,
                            allow=form.allow)
    return jsonify()


@bp.route('/<id_>/alter-ducks', methods=['POST'])
@perm(node='auth.duck')
def alter_ducks(id_):
    form = AlterDuck()
    ducks, confilcts = PinkMgr(id_).alter_ducks(add=form.add, remove=form.remove)
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


@bp.route('/<pink>/<node>/alter-scopes', methods=['POST'])
@perm(node='auth.duck')
def alter_scopes(pink, node):
    form = AlterScopes()
    duck = DuckMgr(pink, node)
    if form.method == AlterScopes.Method.diff:
        duck.add_scopes(scopes=form.positive)
        final = duck.remove_scopes(scopes=form.negative)
    else:
        final = duck.alter_scopes(scopes=form.positive)
    return jsonify({'new_scopes': final})
