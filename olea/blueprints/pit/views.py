from flask import jsonify, request

from olea.auth import login, opt_perm, perm

from . import bp
from .forms import Search
from .services import PitMgr, PitQuery


@bp.route('/<id_>', methods=['GET'])
@opt_perm
def single(id_):
    pit = PitQuery.single(id_)
    return jsonify({'id': pit.id})


@bp.route('/', methods=['GET'])
@opt_perm
def search():
    form = Search(data=request.args)
    pits = PitQuery.search(deps=form.deps, pink_id=form.pink_id)
    return jsonify({})


@bp.route('/<id_>/c-download', methods=['GET'])
@perm(node='pit.check')
def checker_download(id_):
    return jsonify({'share_id': PitMgr(id_).checker_download()})


@bp.route('/<id_>/download', methods=['GET'])
@opt_perm
def download(id_):
    return jsonify({'share_id': PitMgr(id_).download()})


@bp.route('/<id_>/check-pass', methods=['POST'])
@perm(node='pit.check')
def check_pass(id_):
    PitMgr(id_).check_pass()
    return jsonify({})


@bp.route('/<id_>/check-fail', methods=['POST'])
@perm(node='pit.check')
def check_fail(id_):
    PitMgr(id_).check_fail()
    return jsonify({})
