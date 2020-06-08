from flask import g, jsonify

from olea.auth import login_req, permission_required

from . import bp
from .forms import Create, ModifyRoles, SimpleCreate
from .services import ProjMgr


@bp.route('/<id_>/modify_roles', methods=['POST'])
@login_required
def modify_roles(id_: str):
    form = ModifyRoles()
    ProjMgr(id_).modify_roles(add=form.add, remove=form.remove)
    return jsonify({})


@bp.route('/s_create', methods=['POST'])
@login_required
def simple_create():
    form = SimpleCreate()
    proj = ProjMgr.create(base=form.base, type_=form.type, suff='', leader_id=g.pink_id)
    return jsonify({'id': proj.id})


@bp.route('/create', methods=['POST'])
@permission_required
def create():
    form = Create()
    proj = ProjMgr.create(base=form.base, type_=form.type, suff=form.suff, leader_id=form.leader)
    return jsonify({'id': proj.id})
