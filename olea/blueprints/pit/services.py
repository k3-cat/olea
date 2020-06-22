import datetime

from flask import g

from models import Mango, Pit, Proj, Role
from olea.base import BaseMgr
from olea.dep_graph import DepGraph
from olea.errors import AccessDenied, DoesNotMeetRequirements, FileExist, FileVerConflict
from olea.singleton import db, onedrive, pat, redis

from .quality_control import CheckFailed, check_file_meta
from .utils import check_owner, check_state

dep_graph = DepGraph()


class RoleMgr(BaseMgr):
    module = Role

    def drop(self):
        self.o.taken = False


class PitMgr(BaseMgr):
    model = Pit

    def __init__(self, obj_or_id):
        self.o: Pit = None
        super().__init__(obj_or_id)

    @check_owner
    @check_state(set(Pit.S) - {Pit.S.droped, Pit.S.auditing, Pit.S.fin, Pit.S.fin_p})
    def drop(self):
        if self.o.state == Pit.S.init:
            db.session.delete(self.o)
            return True

        self.o.state = Pit.S.droped
        self.o.add_track(info=Pit.T.drop, now=g.now)
        RoleMgr(self.o.role).drop()
        return True

    @check_owner
    @check_state({Pit.S.working, Pit.S.past_due, Pit.S.delayed})
    def submit(self, share_id):
        if g.now > self.o.due or self.o.state == Pit.S.past_due:
            redis.set(f'pstate-{self.o.id}', 'past-due')

        self.o.state = Pit.S.auditing
        self.o.add_track(info=Pit.T.submit, now=g.now)
        mango = MangoMgr.create(self.o, share_id)

        return mango

    @classmethod
    def force_submit(cls, token):
        head, payload = pat.decode_with_head(token)
        pit = cls.model.query.get(head['p'])

        submit_time = datetime.datetime.fromtimestamp(head['t'])
        if submit_time <= pit.due and pit.state == Pit.S.past_due:
            PitMgr(pit)._resume_state()
        elif submit_time > pit.due or pit.state == Pit.S.past_due:
            redis.set(f'pstate-{pit.id}', 'past-due')

        pit.state = Pit.S.auditing
        pit.add_track(info=Pit.T.submit_f, now=submit_time, by=g.pink_id)
        mango = MangoMgr.f_create(pit, share_id=payload['share_id'], sha1=payload['sha1'])

        return mango

    def past_due(self):
        redis.set(f'pstate-{self.o.id}', 'past-due')
        self.o.state = Pit.S.past_due
        self.o.add_track(info=Pit.T.past_due, now=g.now, by=g.pink_id)

    def _resume_state(self):
        state = redis.get(f'pstate-{self.o.id}')
        if not state:
            self.o.state = Pit.S.working
        if state == 'delayed':
            self.o.state = Pit.S.delayed
        elif state == 'past-due':
            self.o.state = Pit.S.past_due

        else:
            raise Exception('BAD RECORD')

    @check_owner
    @check_state({Pit.S.auditing})
    def redo(self):
        self._resume_state()
        self.o.add_track(info=Pit.T.redo, now=g.now)

    def _download(self):
        return onedrive.share(self.o.mango.id)

    @check_state({Pit.S.fin, Pit.S.fin_p})
    def download(self):
        if self.o.pink_id == g.pink_id or g.check_opt_duck(scopes={self.o.role.dep}):
            return self._download()

        roles = Role.query.join(Pit). \
            filter(Pit.pink_id == g.pink_id). \
            filter(Pit.state.in_({Pit.S.pending, Pit.S.working, Pit.S.auditing})). \
            filter(Role.proj_id == self.o.role.proj_id). \
            all()

        if not dep_graph.is_depend_on(own={role.dep for role in roles}, target=self.o.role.dep):
            raise AccessDenied(obj=self.o.mango)

        return self._download()

    @check_state({Pit.S.auditing})
    def checker_download(self):
        return self._download()

    @check_state({Pit.S.auditing})
    def check_fail(self):
        if 0 < (self.o.due - g.now).days < 3:
            redis.set(f'pstate-{self.o.id}', 'delayed')
            # sequence of the following two statements MUST NOT BE CHANGED
            self.o.add_track(info=Pit.T.extend, now=g.now)
            self.o.due = g.now + datetime.timedelta(days=3)

        self._resume_state()
        self.o.add_track(info=Pit.T.check_fail, now=g.now, by=g.pink_id)

    @check_state({Pit.S.auditing})
    def check_pass(self):
        state = redis.get(f'pstate-{self.o.id}')
        if not state or state != 'past-due':
            self.o.state = Pit.S.fin
        else:
            self.o.state = Pit.S.fin_p
        redis.delete(f'pstate-{self.o.id}')

        self.o.finish_at = g.now
        self.o.add_track(info=Pit.T.check_pass, now=g.now, by=g.pink_id)

        ProjMgr(self.o.role.pink_id).post_works()


class ProjMgr(BaseMgr):
    model = Proj

    def __init__(self, obj_or_id):
        self.o: Proj = None
        super().__init__(obj_or_id)

    def post_works(self, pit):
        # check if all pits in this department are done
        exists = Pit.query.join(Role). \
            filter(Role.dep == pit.role.dep). \
            filter(Role.proj_id == self.o.id). \
            filter(~Pit.state.in_({Pit.S.fin, Pit.S.fin_p, Pit.S.droped})). \
            exists()
        if not db.session.query(exists).scalar():
            return

        # alter start and due for the subsequent departments
        extended = pit.finish_at \
            - dep_graph.get_finish_time(base=self.o.start_at, dep=pit.role.dep)
        pits = Pit.query.join(Role). \
            filter(Role.dep.in_(dep_graph.I_RULE[pit.role.dep])). \
            filter(Role.proj_id == self.o.id). \
            all()
        for pit_ in pits:
            pit_.state = Pit.S.working

            # sequence of the following block MUST NOT BE CHANGED
            if (extended_seconds := extended.seconds) < -86400:
                # finished before 1 day prior to due
                pit_.add_track(info=Pit.T.shift, by=pit.id)
                pit_.start_at += extended_seconds
                pit_.due += extended_seconds

            elif extended.seconds > 0:
                # pit is extended
                pit_.add_track(info=Pit.T.cascade, by=pit.id)
                pit_.due += extended_seconds

        # check if proj can upload
        if not pits:
            # all pits in this dep are done + no further pits to fill = project can upload
            self._upload()

    def _upload(self):
        self.o.state = Proj.S.upload
        self.o.add_track(info=Proj.T.upload, now=g.now)


class MangoMgr(BaseMgr):
    model = Mango

    def __init__(self, obj_or_id):
        self.o: Mango = None
        super().__init__(obj_or_id)

    @staticmethod
    def create(pit, share_id):
        i = onedrive.get_shared_item_info(share_id=share_id)
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
        i = onedrive.get_shared_item_info(share_id=share_id)
        if sha1 != i['sha1']:
            raise FileVerConflict(req_sha1=i['sha1'])

        MangoMgr._create(pit, i)

    @classmethod
    def _create(cls, pit, i):
        if mango := cls.model.query.filter_by(sha1=i['sha1']):
            raise FileExist(pit=mango.pit)

        if last := pit.mangos.first():
            onedrive.delete(item_id=last.id)
        ref = onedrive.copy_from_share(drive_id=i['drive_id'],
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
