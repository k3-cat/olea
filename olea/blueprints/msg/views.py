from flask import jsonify, request

from olea.auth import perm

from . import bp
from .forms import Post, Search, Edit
from .query import AnnQuery
from .services import AnnMgr


@bp.route('/', methods=['GET'])
def search():
    form = Search(data=request.args)
    anns = AnnQuery.search(deps=form.deps)
    return jsonify({})


@bp.route('/post', methods=['Post'])
@perm
def post_():
    form = Post()
    ann = AnnMgr.post(cat=form.cat, deps=form.deps, expire_at=form.expire_at, content=form.content)
    return jsonify({})


@bp.route('/<id_>/edit', methods=['Post'])
@perm
def edit(id_):
    form = Edit()
    ann = AnnMgr(id_).edit(content=form.content)
    return jsonify({})


@bp.route('/<id_>/delete', methods=['Post'])
@perm
def delete_(id_):
    pits = AnnMgr(id_).delete()
    return jsonify({})
