from flask import jsonify

from olea.auth import login_required

from . import bp
from .services import PitMgr


@bp.route('/<id_>/check_download', methods=['GET'])
# TODO: permission
@login_required
def check_download(id_):
    return jsonify({'share_id': PitMgr(id_).check_download()})


@bp.route('/<id_>/s_download', methods=['GET'])
@login_required
def simple_download(id_):
    return jsonify({'share_id': PitMgr(id_).simple_download()})


@bp.route('/<id_>/download', methods=['GET'])
# TODO: permission
@login_required
def download(id_):
    return jsonify({'share_id': PitMgr(id_).download()})


@bp.route('/<id_>/check_pass', methods=['POST'])
# TODO: permission
@login_required
def check_pass(id_):
    PitMgr(id_).check_pass()
    return jsonify({})


@bp.route('/<id_>/check_fail', methods=['POST'])
# TODO: permission
@login_required
def check_fail(id_):
    PitMgr(id_).check_fail()
    return jsonify({})
