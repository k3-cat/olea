from flask import jsonify

from olea.auth import login_required
from olea.exts import pat

from . import bp
from .forms import ForceSubmit, Pick, Submit
from .services import PitMgr, RoleMgr


@bp.route('/<id_>/s_pick', methods=['POST'])
@login_required
def simple_pick_role(id_):
    pit = RoleMgr(id_).simple_pick()
    return jsonify({'id': pit.id})


@bp.route('/<id_>/pick', methods=['POST'])
# TODO: permission
@login_required
def pick_role(id_):
    form = Pick()
    pit = RoleMgr(id_).pick(pink=form.pink_id)
    return jsonify({'id': pit.id})


@bp.route('/<id_>/drop', methods=['POST'])
@login_required
def drop_pit(id_):
    pit = PitMgr(id_).drop()
    return jsonify({'id': pit.id})


@bp.route('/<id_>/redo', methods=['POST'])
@login_required
def redo_pit(id_):
    pit = PitMgr(id_).redo()
    return jsonify({'id': pit.id})


@bp.route('/<id_>/submit', methods=['POST'])
@login_required
def submit_pit(id_):
    form = Submit()
    pit = PitMgr(id_).submit(share_id=form.share_id)
    return jsonify({'id': pit.id})


@bp.route('/f_submit', methods=['POST'])
# TODO: permission
@login_required
def force_submit_pit():
    form = ForceSubmit()
    head, payload = pat.decode_with_head(form.token)
    pit = PitMgr(head['p'], europaea=True).force_submit(t=head['t'],
                                                        share_id=payload['id'],
                                                        sha1=payload['sha1'])
    return jsonify({'id': pit.id})
