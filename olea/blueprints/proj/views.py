from flask import g, jsonify

from olea.auth import login, perm

from . import bp
from .forms import Create, FullCreate, ModifyRoles
from .services import ProjMgr


@bp.route('/<id_>/modify-roles', methods=['POST'])
@login
def modify_roles(id_: str):
    form = ModifyRoles()
    roles = ProjMgr(id_).modify_roles(add=form.add, remove=form.remove)
    return jsonify({role.id: role.name for role in roles})


@bp.route('/<id_>/f-modify-roles', methods=['POST'])
@perm
def force_modify_roles(id_: str):
    form = ModifyRoles()
    roles = ProjMgr(id_).force_modify_roles(add=form.add, remove=form.remove)
    return jsonify({role.id: role.name for role in roles})


@bp.route('/create', methods=['POST'])
@login
def create():
    form = Create()
    proj = ProjMgr.create(base=form.base, type_=form.type, suff='', leader_id=g.pink_id)
    return jsonify({'id': proj.id})


@bp.route('/f-create', methods=['POST'])
@perm
def full_create():
    form = FullCreate()
    proj = ProjMgr.create(base=form.base, type_=form.type, suff=form.suff, leader_id=form.leader)
    return jsonify({'id': proj.id})
