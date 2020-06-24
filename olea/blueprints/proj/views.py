from flask import g, jsonify, request

from olea.auth import opt_perm, perm

from . import bp
from .forms import Create, Finish, FullCreate, ModifyRoles, Pick, Search
from .query import ProjQuery
from .services import ProjMgr, RoleMgr


@bp.route('/<id_>', methods=['GET'])
@opt_perm
def single(id_):
    proj = ProjQuery.single(id_)
    return jsonify({'id': proj.id})


@bp.route('/', methods=['GET'])
@opt_perm
def search():
    form = Search(request.args)
    projs = ProjQuery.search(states=form.states, cats=form.cats)
    return jsonify({})


@bp.route('/create', methods=['POST'])
def create():
    form = Create()
    proj = ProjMgr.create(base=form.base, cat=form.cat, suff='', leader_id=g.pink_id)
    return jsonify({'id': proj.id})


@bp.route('/f-create', methods=['POST'])
@perm
def full_create():
    form = FullCreate()
    proj = ProjMgr.create(base=form.base, cat=form.cat, suff=form.suff, leader_id=form.leader)
    return jsonify({'id': proj.id})


@bp.route('/<id_>/modify-roles', methods=['POST'])
def modify_roles(id_: str):
    form = ModifyRoles()
    roles = ProjMgr(id_).modify_roles(add=form.add, remove=form.remove)
    return jsonify({role.id: {'name': role.name, 'dep': role.dep.name} for role in roles})


@bp.route('/<id_>/start', methods=['POST'])
def start(id_):
    ProjMgr(id_).start()
    return jsonify()


@bp.route('/<id_>/finish', methods=['POST'])
@perm
def finish(id_):
    form = Finish()
    ProjMgr(id_).finish(url=form.url)
    return jsonify()


@bp.route('/roles/<role_id>/pick', methods=['POST'])
def pick(role_id):
    pit = RoleMgr(role_id).pick()
    return jsonify({'id': pit.id})


@bp.route('/roles/<role_id>/f-pick', methods=['POST'])
@perm
def full_pick(role_id):
    form = Pick()
    pit = RoleMgr(role_id).full_pick(pink_id=form.pink_id)
    return jsonify({'id': pit.id})
