from models import Proj
from core.auth import check_opt_duck
from core.base import single_query
from core.errors import AccessDenied


def proj_serializer(proj: Proj):
    picture_count = 0
    audio_duration = 0
    video_duration = 0

    for role in proj.roles:
        mango = role.pit.mango

        if mango.mtype == 'image':
            picture_count += 1

        if mango.mtype == 'audio':
            audio_duration += mango.metainfo['duration']

        if mango.mtype == 'video':
            video_duration += mango.metainfo['duration']

    result = proj.__json__()
    result['picture_count'] = picture_count
    result['audio_duration'] = audio_duration
    result['video_duration'] = video_duration

    return result


class ProjQuery():
    PUBLIC_STATUS = {Proj.S.working, Proj.S.pre, Proj.S.upload}

    @classmethod
    def single(cls, id_):
        proj = single_query(model=Proj,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.status in cls.PUBLIC_STATUS)
        return proj_serializer(proj)

    @classmethod
    def search(cls, status_set=None, cats=None):
        if status_set - cls.PUBLIC_STATUS and not check_opt_duck():
            raise AccessDenied(cls_=Proj)
        query = Proj.query.filter(Proj.status.in_(status_set))
        if cats:
            query.filter(Proj.cat.in_(cats))
        return query.all()
