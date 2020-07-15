from flask import g
from flask_json import json_response

from olea.auth import opt_perm, perm

from . import bp
from .forms import Create, Finish, FullCreate, ModifyRoles, Pick, Search
from .query import ProjQuery
from .services import ProjMgr, RoleMgr


@bp.route('/<id_>', methods=['GET'])
@opt_perm()
def get_id(id_):
    proj = ProjQuery.single(id_)
    return json_response(data_=proj)


@bp.route('/', methods=['GET'])
@opt_perm()
def search():
    form = Search()
    projs = ProjQuery.search(status_set=form.status_set, cats=form.cats)
    return json_response(data_=projs)


@bp.route('/create', methods=['POST'])
def create():
    form = Create()
    proj = ProjMgr.create(base=form.base, cat=form.cat, suff='', leader_id=g.pink_id)
    return json_response(data_=proj)


@bp.route('/f-create', methods=['POST'])
@perm()
def full_create():
    form = FullCreate()
    proj = ProjMgr.create(base=form.base, cat=form.cat, suff=form.suff, leader_id=form.leader)
    return json_response(data_=proj)


@bp.route('/<id_>/modify-roles', methods=['POST'])
def modify_roles(id_: str):
    form = ModifyRoles()
    roles = ProjMgr(id_).modify_roles(add=form.add, remove=form.remove)
    return json_response(data_=roles)


@bp.route('/<id_>/start', methods=['POST'])
def start(id_):
    ProjMgr(id_).start()
    return json_response()


@bp.route('/<id_>/finish', methods=['POST'])
@perm()
def finish(id_):
    form = Finish()
    ProjMgr(id_).finish(url=form.url)
    return json_response()


@bp.route('/roles/<role_id>/pick', methods=['POST'])
def pick(role_id):
    pit = RoleMgr(role_id).pick()
    return json_response(data_=pit)


@bp.route('/roles/<role_id>/f-pick', methods=['POST'])
@perm()
def full_pick(role_id):
    form = Pick()
    pit = RoleMgr(role_id).full_pick(pink_id=form.pink_id)
    return json_response(data_=pit)
