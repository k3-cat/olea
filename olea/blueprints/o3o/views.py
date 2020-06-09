from flask import jsonify

from olea.auth import login, perm
from olea.exts import pat

from . import bp
from .forms import ForceSubmit, Pick, Submit
from .services import PitMgr, RoleMgr


@bp.route('/<id_>/pick', methods=['POST'])
@login
def pick(id_):
    pit = RoleMgr(id_).pick()
    return jsonify({'id': pit.id})


@bp.route('/<id_>/f-pick', methods=['POST'])
@perm
def full_pick(id_):
    form = Pick()
    pit = RoleMgr(id_).full_pick(pink=form.pink_id)
    return jsonify({'id': pit.id})


@bp.route('/<id_>/drop', methods=['POST'])
@login
def drop(id_):
    pit = PitMgr(id_).drop()
    return jsonify({'id': pit.id})


@bp.route('/<id_>/redo', methods=['POST'])
@login
def redo(id_):
    pit = PitMgr(id_).redo()
    return jsonify({'id': pit.id})


@bp.route('/<id_>/submit', methods=['POST'])
@login
def submit(id_):
    form = Submit()
    pit = PitMgr(id_).submit(share_id=form.share_id)
    return jsonify({'id': pit.id})


@bp.route('/f-submit', methods=['POST'])
@perm
def force_submit():
    form = ForceSubmit()
    head, payload = pat.decode_with_head(form.token)
    pit = PitMgr(head['p'], europaea=True).force_submit(t=head['t'],
                                                        share_id=payload['id'],
                                                        sha1=payload['sha1'])
    return jsonify({'id': pit.id})
