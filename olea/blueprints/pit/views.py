from flask import request
from flask_json import json_response

from olea.auth import opt_perm, perm

from . import bp
from .forms import Checks, ForceSubmit, Search, InDep, Submit
from .query import PitQuery
from .services import PitMgr


@bp.route('/<id_>', methods=['GET'])
@opt_perm
def single(id_):
    pit = PitQuery.single(id_)
    return json_response(data_=pit)


@bp.route('/in_dep/', methods=['GET'])
@perm(node='pit.in_dep.all')
def in_dep():
    form = InDep()
    pits = PitQuery.in_dep(dep=form.dep, status=form.status_set)
    return json_response(data_=pits)


@bp.route('/checks/', methods=['GET'])
@perm(node='pit.check')
def checks():
    form = Checks()
    pits = PitQuery.check_list(deps=form.deps)
    return json_response(data_=pits)


@bp.route('/', methods=['GET'])
@opt_perm
def search():
    form = Search()
    pits = PitQuery.search(deps=form.deps, status_set=form.status_set, pink_id=form.pink_id)
    return json_response(data_=pits)


@bp.route('/<id_>/drop', methods=['POST'])
def drop(id_):
    PitMgr(id_).drop()
    return json_response()


@bp.route('/<id_>/submit', methods=['POST'])
def submit(id_):
    form = Submit()
    PitMgr(id_).submit(share_id=form.share_id)
    return json_response()


@bp.route('/<id_>/f-submit', methods=['POST'])
@perm
def force_submit(id_):
    form = ForceSubmit()
    PitMgr(id_).force_submit(token=form.token)
    return json_response()


@bp.route('/<id_>/redo', methods=['POST'])
def redo(id_):
    PitMgr(id_).redo()
    return json_response()


@bp.route('/<id_>/download', methods=['GET'])
@opt_perm
def download(id_):
    share_id = PitMgr(id_).download()
    return json_response(share_id=share_id)


@bp.route('/<id_>/c-download', methods=['GET'])
@perm(node='pit.check')
def checker_download(id_):
    share_id = PitMgr(id_).checker_download()
    return json_response(share_id=share_id)


@bp.route('/<id_>/check-pass', methods=['POST'])
@perm(node='pit.check')
def check_pass(id_):
    PitMgr(id_).check_pass()
    return json_response()


@bp.route('/<id_>/check-fail', methods=['POST'])
@perm(node='pit.check')
def check_fail(id_):
    PitMgr(id_).check_fail()
    return json_response()
