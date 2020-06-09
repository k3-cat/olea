from flask import jsonify

from olea.auth import login, perm

from . import bp
from .services import PitMgr


@bp.route('/<id_>/c-download', methods=['GET'])
@perm(node='pit.check')
def checker_download(id_):
    return jsonify({'share_id': PitMgr(id_).checker_download()})


@bp.route('/<id_>/download', methods=['GET'])
@login
def download(id_):
    return jsonify({'share_id': PitMgr(id_).download()})


@bp.route('/<id_>/f-download', methods=['GET'])
@perm
def force_download(id_):
    return jsonify({'share_id': PitMgr(id_).force_download()})


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
