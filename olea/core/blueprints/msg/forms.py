from flask_jsonapi import BaseForm
from json_api.fields import DateTime, Enum, Integer, Set, String

from models import Ann, Dep


class FetchAnn(BaseForm):
    deps = Set(Enum(Dep), default=set(Dep))


class PostAnn(BaseForm):
    level = Enum(Ann.L)
    deps = Set(Enum(Dep))
    expiration = DateTime
    content = String


class Edit(BaseForm):
    content = String


class ChatLogs(BaseForm):
    offset = Integer


class PostChat(BaseForm):
    reply_to_id = String
    content = String


class FetchChat(BaseForm):
    chats = Set(String)
