from flask import g, jsonify, request

from olea.auth import login, opt_perm, perm

from . import bp
from .forms import Create, ResetPwdF, ResetPwdI, Search, SetPwd, UpdateInfo
from .services import PinkMgr, PinkQuery


@bp.route('/<id_>', methods=['GET'])
def single(id_):
    pink = PinkQuery.single(id_)
    return jsonify({})


@bp.route('/', methods=['GET'])
def search():
    form = Search(request.args)
    pinks = PinkQuery.search(deps=form.deps, name=form.name, qq=form.qq)
    return pinks


@bp.route('/info', methods=['GET'])
def info():
    return jsonify(g.pink.to_dict(lv=2))


@bp.route('/update-info', methods=['POST'])
def update_info():
    form = UpdateInfo()
    PinkMgr(g.pink_id).update_info(qq=form.qq, other=form.other, email=form.email)
    return 'True'


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
