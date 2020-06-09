import datetime

from flask import g

from models import Dep, Mango, Pink, Pit, PitState, Role
from olea.errors import (AccessDenied, DoesNotMeetRequirements, DuplicatedRecord, FileVerConflict,
                         NotQualifiedToPick, RoleIsTaken, UnallowedType)
from olea.exts import db, onerive, pat

from ..base_mgr import BaseMgr
from ..pit.utils import check_state
from .quality_control import CheckFailed, check_file_meta


class RoleMgr(BaseMgr):
    model = Role

    def full_pick(self, pink_id):
        if self.o.taken:
            raise RoleIsTaken(by=self.o.pit)
        self.o.taken = True
        pit = PitMgr.create(self.o, pink_id)
        if pink_id != g.pink_id:
            pit.add_track(info=Pit.Trace.pick_f, now=g.now, by=g.pink_id)
        return pit

    def pick(self):
        pink = Pink.query().get(g.pink_id)
        if self.o.dep not in pink.deps:
            raise NotQualifiedToPick(dep=self.o.dep)
        return self.full_pick(pink.id)

    def drop(self):
        self.o.taken = False


class PitMgr(BaseMgr):
    model = Pit

    def __init__(self, obj_or_id, europaea=False):
        super().__init__(obj_or_id)
        if not europaea and self.o.pink_id != g.pink_id:
            raise AccessDenied(obj=self.o)

    @classmethod
    def create(cls, role, pink_id):
        pit = cls.model(id=cls.gen_id(), role=role, pink_id=pink_id, timestamp=g.now)
        db.session.add(pit)
        return pit

    def delete(self):
        db.session.delete(self.o)
        return True

    def drop(self):
        if self.o.state == PitState.init:
            self.delete()
            return True

        check_state(self.o.state, (PitState.working, ))
        self.o.state = PitState.droped
        self.o.add_track(info=Pit.Trace.drop, now=g.now)
        RoleMgr(self.o.role).drop()
        return True

    def force_drop(self):
        self.o.state = PitState.droped_f
        self.o.add_track(info=Pit.Trace.drop_f, now=g.now, by=g.pink_id)
        RoleMgr(self.o.role).drop()
        return True

    def submit(self, share_id):
        check_state(self.o.state, (PitState.working, PitState.delayed))
        self.o.state = PitState.auditing
        self.o.add_track(info=Pit.Trace.submit, now=g.now)
        mango = MangoMgr.create(self.o, share_id)
        return mango

    @classmethod
    def force_submit(cls, token):
        head, payload = pat.decode_with_head(token)
        pit = cls.query(head['p'])
        check_state(pit.state, (PitState.working, PitState.delayed, PitState.droped_f))
        pit.state = PitState.auditing
        pit.add_track(info=Pit.Trace.submit_f,
                      now=datetime.datetime.fromtimestamp(payload['t']),
                      by=g.pink_id)
        mango = MangoMgr.f_create(pit, share_id=payload['share_id'], sha1=payload['sha1'])
        return mango

    def redo(self):
        check_state(self.o.state, (PitState.auditing, ))
        self.o.state = PitState.working
        self.o.add_track(info=Pit.Trace.redo, now=g.now)


class MangoMgr(BaseMgr):
    model = Mango

    @staticmethod
    def create(pit, share_id):
        i = onerive.get_shared_item_info(share_id=share_id)
        try:
            check_file_meta(pit.role.dep, i)
        except CheckFailed as e:
            token = pat.encode(exp=86400 * 3,
                               payload={
                                   'id': share_id,
                                   'sha1': i['sha1'],
                                   'confl': e.confl
                               },
                               head={
                                   'p': pit.id,
                                   't': g.now.timestamp()
                               })
            raise DoesNotMeetRequirements(confl=e.confl, required=e.required, token=token)

        MangoMgr._create(pit, i)

    @staticmethod
    def f_create(pit, share_id, sha1):
        i = onerive.get_shared_item_info(share_id=share_id)
        if sha1 != i['sha1']:
            raise FileVerConflict(req_sha1=i['sha1'])

        MangoMgr._create(pit, i)

    @classmethod
    def _create(cls, pit, i):
        if mango := cls.query().filter_by(sha1=i['sha1']):
            raise DuplicatedRecord(obj=mango)

        if last := pit.mango:
            onerive.delete(item_id=last.id)
        ref = onerive.copy_from_share(drive_id=i['drive_id'],
                                      item_id=i['id'],
                                      name=f'{pit.id}.{i["name"].split(".")[-1]}')

        mango = cls.model(id=ref,
                          pit_id=pit.id,
                          ver=1 if not last else last.ver + 1,
                          mime=i['mime'],
                          sha1=i['sha1'],
                          modified_at=i['last_modify'],
                          timestamp=g.now,
                          metainfo=i['metainfo'])
        db.session.add(mango)

        return mango
