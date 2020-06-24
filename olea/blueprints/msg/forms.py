from flask_jsonapi import BaseForm
from json_api.fields import Set, String, Enum, DateTime, Integer
from models import Ann, Dep


class FetchAnn(BaseForm):
    deps = Set(Enum(Dep), default=set([dep.name for dep in Dep]))


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
