from flask import g, jsonify

from olea.auth import login_required, permission_required

from . import bp
from .forms import Create, SetPwd, UpdateInfo
from .services import PinkMgr


@bp.route('/<id_>/get', methods=['GET'])
@login_required
def get_pink(id_: str):
    return jsonify(query_pink(id_).to_dict(lv=1))


@bp.route('/info', methods=['GET'])
@login_required
def info():
    return jsonify(g.pink.to_dict(lv=2))


@bp.route('/update_info', methods=['POST'])
@login_required
def update_info():
    form = UpdateInfo()
    PinkMgr(g.pink_id).update_info(qq=form.qq, other=form.other, email=form.email)
    return 'True'


@bp.route('/create', methods=['POST'])
@permission_required(perm='pink.create')
def create():
    form = Create()
    pink = PinkMgr.create(
        name=form.name,
        qq=form.qq,
        other=form.other,
        email=form.email,
        deps=form.deps,
    )
    return jsonify({'id': pink.id})


@bp.route('/reset_pwd', methods=['POST'])
@permission_required(perm='pink.reset_pwd')
def reset_pwd():
    PinkMgr(g.pink_id).reset_pwd()
    return jsonify({})


@bp.route('/set_pwd', methods=['POST'])
@login_required
def set_pwd():
    form = SetPwd()
    PinkMgr(g.pink_id).set_pwd(form.pwd)
    return jsonify({})


@bp.route('/<id_>/deactive', methods=['POST'])
@permission_required(perm='pink.deative')
def deactive(id_):
    PinkMgr(id_).deactive()
    return jsonify({})
