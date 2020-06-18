from flask import jsonify, request

from olea.auth import opt_perm, perm

from . import bp
from .forms import Checks, ForceSubmit, Search, SearchMy, Submit
from .query import PitQuery
from .services import PitMgr


@bp.route('/<id_>', methods=['GET'])
@opt_perm
def single(id_):
    pit = PitQuery.single(id_)
    return jsonify({'id': pit.id})


@bp.route('/my', methods=['GET'])
def my():
    form = SearchMy(data=request.args)
    pits = PitQuery.my(deps=form.deps, states=form.states)
    return jsonify({})


@bp.route('/checks/', methods=['GET'])
@perm(node='pit.check')
def checks():
    form = Checks(data=request.args)
    pits = PitQuery.check_list(deps=form.deps)
    return jsonify({})


@bp.route('/', methods=['GET'])
@perm
def search():
    form = Search(data=request.args)
    pits = PitQuery.search_all(deps=form.deps, states=form.states, pink_id=form.pink_id)
    return jsonify({})


@bp.route('/<id_>/drop', methods=['POST'])
def drop(id_):
    pit = PitMgr(id_).drop()
    return jsonify({})


@bp.route('/<id_>/submit', methods=['POST'])
def submit(id_):
    form = Submit()
    pit = PitMgr(id_).submit(share_id=form.share_id)
    return jsonify({'id': pit.id})


@bp.route('/f-submit', methods=['POST'])
@perm
def force_submit():
    form = ForceSubmit()
    pit = PitMgr.force_submit(token=form.token)
    return jsonify({'id': pit.id})


@bp.route('/<id_>/redo', methods=['POST'])
def redo(id_):
    pit = PitMgr(id_).redo()
    return jsonify({'id': pit.id})


@bp.route('/<id_>/download', methods=['GET'])
@opt_perm
def download(id_):
    return jsonify({'share_id': PitMgr(id_).download()})


@bp.route('/<id_>/c-download', methods=['GET'])
@perm(node='pit.check')
def checker_download(id_):
    return jsonify({'share_id': PitMgr(id_).checker_download()})


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
