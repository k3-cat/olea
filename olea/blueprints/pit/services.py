import datetime
from functools import wraps

from flask import g

from models import Dep, Mango, Pit, Proj, Role
from olea.base import BaseMgr, single_query
from olea.errors import (AccessDenied, DoesNotMeetRequirements, FileExist, FileVerConflict,
                         RecordNotFound, StateLocked)
from olea.exts import db, onerive, redis
from olea.singleton import pat

from .quality_control import CheckFailed, check_file_meta


class PitQuery():
    @staticmethod
    def single(id_):
        return single_query(model=Pit,
                            id_or_obj=id_,
                            condiction=lambda obj: obj.pink_id == g.pink_id)

    SEARCH_ALL = {Pit.State.working, Pit.State.past_due, Pit.State.delayed, Pit.State.auditing}
    MY = {
        Pit.State.init, Pit.State.working, Pit.State.past_due, Pit.State.auditing,
        Pit.State.delayed, Pit.State.droped
    }
    ALL_DEP = {Dep.ae, Dep.au, Dep.ps}

    @classmethod
    def check_list(cls, deps):
        deps = deps & cls.ALL_DEP if deps else cls.ALL_DEP
        if not g.check_scope(scope=deps):
            raise AccessDenied(cls=Pit)

        pits = Pit.query.join(Role) \
            .filter(Pit.state == Pit.State.auditing) \
            .filter(Role.dep.in_(deps)).all()

        return pits

    @classmethod
    def my(cls, deps, states):
        deps = deps & cls.ALL_DEP if deps else cls.ALL_DEP

        pits = Pit.query.join(Role) \
            .filter(Pit.state.in_(states & cls.MY)) \
            .filter(Pit.pink_id == g.pink_id) \
            .filter(Role.dep.in_(deps)).all()

        return pits

    @classmethod
    def search_all(cls, deps, states, pink_id=''):
        deps = deps & cls.ALL_DEP if deps else cls.ALL_DEP

        if not g.check_scope(scope=deps):
            raise AccessDenied(cls=Pit)

        query = Pit.query.join(Role) \
            .filter(Pit.state.in_(states & cls.SEARCH_ALL))
        if pink_id:
            query = query.filter(Pit.pink_id == pink_id)
        pits = query.filter(Role.dep.in_(deps)).all()

        return pits


class RoleMgr(BaseMgr):
    module = Role

    def drop(self):
        self.o.taken = False


class PitMgr(BaseMgr):
    model = Pit

    ALLOWED_DEPS = {
        Dep.ps: {Dep.ae},
        Dep.au: {Dep.ae},
    }

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    def check_owner(self):
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if self.o.pink_id != g.pink_id:
                    raise AccessDenied(obj=self.o)
                return f(*args, **kwargs)

            return wrapper

        return decorate

    def check_state(self, required: Tuple[Pit.State]):
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if self.o.state not in required:
                    raise StateLocked(current=self.o.state, required=required)
                return f(*args, **kwargs)

            return wrapper

        return decorate

    @check_owner
    @check_state({Pit.State.working, Pit.State.init})
    def drop(self):
        if self.o.state == Pit.State.init:
            db.session.delete(self.o)
            return True

        self.o.state = Pit.State.droped
        self.o.add_track(info=Pit.Trace.drop, now=g.now)
        RoleMgr(self.o.role).drop()
        return True

    @check_owner
    @check_state({Pit.State.working, Pit.State.past_due, Pit.State.delayed})
    def submit(self, share_id):
        if g.now > self.o.due or self.o.state == Pit.State.past_due:
            redis.set(f'pstate-{self.o.id}', 'past-due')
        self.o.state = Pit.State.auditing
        self.o.add_track(info=Pit.Trace.submit, now=g.now)
        mango = MangoMgr.create(self.o, share_id)
        return mango

    @classmethod
    def force_submit(cls, token):
        head, payload = pat.decode_with_head(token)
        pit = cls.query.get(head['p'])
        pit.state = Pit.State.auditing
        pit.add_track(info=Pit.Trace.submit_f,
                      now=datetime.datetime.fromtimestamp(payload['t']),
                      by=g.pink_id)
        mango = MangoMgr.f_create(pit, share_id=payload['share_id'], sha1=payload['sha1'])
        return mango

    @check_owner
    @check_state({Pit.State.auditing})
    def redo(self):
        self.o.state = Pit.State.working if self.o.not_past_due() else Pit.State.past_due
        self.o.add_track(info=Pit.Trace.redo, now=g.now)

    def _download(self):
        return onerive.share(self.o.mango.id)

    @check_state({Pit.State.fin, Pit.State.fin_p})
    def download(self):
        if self.o.pink_id == g.pink_id or g.check_opt_duck(scopes={self.o.role.dep}):
            return self._download()
        '''
        sub_query = db.session.query(Pit.role_id) \
            .filter_by(pink_id=g.pink_id) \
            .filter(Pit.state.in_({Pit.State.pending, Pit.State.working, Pit.State.auditing}}) \
            .sub_query()
        roles = Role.query.filter(Role.id.in_(sub_query}).all()
        '''
        roles = Role.query.join(Pit) \
            .filter(Pit.pink_id == g.pink_id) \
            .filter(Pit.state.in_({Pit.State.pending, Pit.State.working, Pit.State.auditing})) \
            .filter(Role.proj_id == self.o.role.proj_id) \
            .all()
        if not self.ALLOWED_DEPS[self.o.role.dep] & {role.dep for role in roles}:
            raise AccessDenied(obj=self.o.mango)
        return self._download()

    @check_state({Pit.State.auditing})
    def checker_download(self):
        return self._download()

    @check_state({Pit.State.auditing})
    def check_pass(self):
        self.o.add_track(info=Pit.Trace.check_pass, now=g.now, by=g.pink_id)

        state = redis.get(f'pstate-{self.o.id}')
        if not state or state != 'past-due':
            self.o.state = Pit.State.fin
        else:
            self.o.state = Pit.State.fin_p

        ProjMgr(self.o.role.pink_id).check_ready_to_upload()

    @check_state({Pit.State.auditing})
    def check_fail(self):
        self.o.add_track(info=Pit.Trace.check_fail, now=g.now, by=g.pink_id)

        state = redis.get(f'pstate-{self.o.id}')
        if not state or state == 'delayed':
            if (self.o.due - g.now).days < 3:
                state = 'delayed'
                redis.set(f'pstate-{self.o.id}', 'delayed')
                self.o.add_track(info=Pit.Trace.extend, now=g.now)
                self.o.due = g.now + datetime.timedelta(days=3)

            if state == 'delayed':
                self.o.state = Pit.State.delayed
            else:
                self.o.state = Pit.State.working

        elif state == 'past-due':
            self.o.state = Pit.State.past_due

        else:
            raise Exception('BAD RECORD')

    def past_due(self):
        # check_state(self.o.state, (Pit.State.working, ))
        self.o.state = Pit.State.past_due
        redis.set(f'pstate-{self.o.id}', 'past-due')
        self.o.add_track(info=Pit.Trace.past_due, now=g.now, by=g.pink_id)
        return True


class ProjMgr(BaseMgr):
    model = Proj

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

    def check_ready_to_upload(self):
        roles = self.o.roles.count()
        finished = Role.query.join(Pit) \
            .filter(Role.proj_id == self.o.id) \
            .filter(Pit.state == Pit.State.fin) \
            .count()
        if roles == finished:
            self._upload()

    def _upload(self):
        self.o.state = Proj.State.upload
        self.o.add_track(info=Proj.Trace.upload, now=g.now)


class MangoMgr(BaseMgr):
    model = Mango

    def __init__(self, obj_or_id):
        self.o: self.model = None
        super().__init__(obj_or_id)

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
                                   'state': pit.state,
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
        if mango := cls.query.filter_by(sha1=i['sha1']):
            raise FileExist(pit=mango.pit)

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
