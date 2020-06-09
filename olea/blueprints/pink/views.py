from flask import g, jsonify

from olea.auth import login, perm

from . import bp
from .forms import Create, ResetPwdF, ResetPwdI, SetPwd, UpdateInfo
from .services import PinkMgr


@bp.route('/<id_>/get', methods=['GET'])
@login
def get_pink(id_: str):
    return jsonify(query_pink(id_).to_dict(lv=1))


@bp.route('/info', methods=['GET'])
@login
def info():
    return jsonify(g.pink.to_dict(lv=2))


@bp.route('/update-info', methods=['POST'])
@login
def update_info():
    form = UpdateInfo()
    PinkMgr(g.pink_id).update_info(qq=form.qq, other=form.other, email=form.email)
    return 'True'


@bp.route('/set-pwd', methods=['POST'])
@login
def set_pwd():
    form = SetPwd()
    PinkMgr(g.pink_id).set_pwd(form.pwd)
    return jsonify({})


@bp.route('/reset-pwd-i', methods=['POST'])
def reset_pwd_i():
    form = ResetPwdI()
    PinkMgr.reset_pwd_init(name=form.name, email=form.email)
    return jsonify({})


@bp.route('/reset-pwd', methods=['POST'])
def reset_pwd():
    form = ResetPwdF()
    PinkMgr.reset_pwd_fin(token=form.token, pwd=form.pwd)
    return jsonify({})


@bp.route('/create', methods=['POST'])
@perm
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


@bp.route('/<id_>/deactive', methods=['POST'])
@perm
def deactive(id_):
    PinkMgr(id_).deactive()
    return jsonify({})
