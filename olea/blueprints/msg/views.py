from flask import jsonify, request

from olea.auth import opt_perm, perm

from . import bp
from .forms import ChatLogs, Edit, FetchAnn, FetchChat, PostAnn, PostChat
from .query import AnnQuery, ChatQuery
from .services import AnnMgr, ChatMgr, ProjMgr


@bp.route('/anns/', methods=['GET'])
def search():
    form = FetchAnn(data=request.args)
    anns = AnnQuery.search(deps=form.deps)
    return jsonify({})


@bp.route('/anns/post', methods=['Post'])
@perm
def post_():
    form = PostAnn()
    ann = AnnMgr.post(cat=form.cat,
                      deps=form.deps,
                      expiration=form.expiration,
                      content=form.content)
    return jsonify({})


@bp.route('/anns/<ann_id>/edit', methods=['Post'])
@perm
def edit(ann_id):
    form = Edit()
    ann = AnnMgr(ann_id).edit(content=form.content)
    return jsonify({})


@bp.route('/anns/<ann_id>/delete', methods=['Post'])
@perm
def delete_(ann_id):
    pits = AnnMgr(ann_id).delete()
    return jsonify({})


@bp.route('/chats/<proj_id>/logs', methods=['GET'])
def chats_index(proj_id):
    form = ChatLogs(data=request.args)
    index = ChatQuery.chat_logs(proj_id=proj_id, offset=form.offset)


@bp.route('/chats/', methods=['GET'])
def chats():
    form = FetchChat(data=request.args)
    chats = ChatQuery.chats(chats=form.chats)


@bp.route('/chats/<proj_id>/post', methods=['POST'])
def post_chat(proj_id):
    form = PostChat()
    chat = ProjMgr(proj_id).post_chat(reply_to_id=form.reply_to_id, content=form.content)
    return jsonify({})


@bp.route('/chats/<chat_id>/edit', methods=['POST'])
def edit_chat(chat_id):
    form = Edit()
    chat = ChatMgr(chat_id).edit(content=form.content)
    return jsonify({})


@bp.route('/chats/<chat_id>/delete', methods=['POST'])
@opt_perm(node='chats.delete')
def delete_chat(chat_id):
    ChatMgr(chat_id).delete()
    return jsonify({})
