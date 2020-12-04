from flask_json import json_response

from core.auth import opt_perm, perm

from . import bp
from .forms import ChatLogs, Edit, FetchAnn, FetchChat, PostAnn, PostChat
from .query import AnnQuery, ChatQuery
from .services import AnnMgr, ChatMgr, ProjMgr


@bp.route('/anns/<id_>', methods=['GET'])
def get_id(id_):
    ann = AnnQuery.single(id_=id_)
    return json_response(data_=ann)


@bp.route('/anns/', methods=['GET'])
def search_anns():
    form = FetchAnn()
    anns = AnnQuery.search(deps=form.deps)
    return json_response(data_=anns)


@bp.route('/anns/post', methods=['POST'])
@perm()
def post_ann():
    form = PostAnn()
    ann = AnnMgr.post(cat=form.cat,
                      deps=form.deps,
                      expiration=form.expiration,
                      content=form.content)
    return json_response(data_=ann)


@bp.route('/anns/<ann_id>/edit', methods=['POST'])
@perm()
def edit_ann(ann_id):
    form = Edit()
    ann = AnnMgr(ann_id).edit(content=form.content)
    return json_response(data_=ann)


@bp.route('/anns/<ann_id>/delete', methods=['Post'])
@perm()
def delete_ann(ann_id):
    AnnMgr(ann_id).delete()
    return json_response()


@bp.route('/chats/<proj_id>/', methods=['GET'])
def chats_index(proj_id):
    form = ChatLogs()
    index = ChatQuery.chat_logs(proj_id=proj_id, offset=form.offset)
    return json_response(data_=index)


@bp.route('/chats/', methods=['GET'])
def get_chats():
    form = FetchChat()
    chats = ChatQuery.chats(chats=form.chats)
    return json_response(data_=chats)


@bp.route('/chats/<proj_id>/post', methods=['POST'])
def post_chat(proj_id):
    form = PostChat()
    chat = ProjMgr(proj_id).post_chat(reply_to_id=form.reply_to_id, content=form.content)
    return json_response(data_=chat)


@bp.route('/chats/<chat_id>/edit', methods=['POST'])
def edit_chat(chat_id):
    form = Edit()
    chat = ChatMgr(chat_id).edit(content=form.content)
    return json_response(data_=chat)


@bp.route('/chats/<chat_id>/delete', methods=['POST'])
@opt_perm(node='chats.delete')
def delete_chat(chat_id):
    ChatMgr(chat_id).delete()
    return json_response()
