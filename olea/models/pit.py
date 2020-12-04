__all__ = ['Pit']

from enum_tools import ZEnum
from sqlalchemy_ import BaseModel, Column, ForeignKey, relationship
from sqlalchemy_.types import ARRAY, DateTime, Enum, String

from .mango import Mango


class Pit(BaseModel):
    __tablename__ = 'pit'

    # Status
    class S(ZEnum):
        init = 'I'
        pending = 'P'
        working = 'w'
        delayed = 'd'
        past_due = 'p'
        auditing = 'a'
        fin = 'F'
        fin_p = 'Fp'
        dropped = 'D'

    id = Column(String, primary_key=True)
    role_id = Column(String, ForeignKey('role.id', ondelete='CASCADE'))
    pink_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    status = Column(Enum(S, name='pit_status'), default=S.init, index=True)
    start_at = Column(DateTime, nullable=True)
    finish_at = Column(DateTime, nullable=True)
    due = Column(DateTime, nullable=True)
    timestamp = Column(DateTime)

    track = Column(ARRAY(String), default=list)

    pink = relationship('Pink', back_populates='pits')
    role = relationship('Role', back_populates='pits')
    mangos = relationship('Mango',
                          back_populates='pit',
                          order_by='Mango.ver.desc()',
                          lazy='dynamic',
                          passive_deletes=True)
    __id_len__ = 13

    @property
    def mango(self):
        return self.mangos.order_by(Mango.ver.desc()).first()

    # Trace
    class T(ZEnum):
        pick_f = 'P'
        drop = 'd'
        shift = '<-'
        cascade = '->'
        past_due = '<>'
        fake_past_due = '><'
        submit = 's'
        submit_f = 'S'
        redo = 'r'
        check_pass = 'o'
        check_fail = 'x'
        extend = '+'

    def add_track(self, info: 'T', now, by=''):
        base = f'{info.value} - {now}'
        if info in (Pit.T.past_due, Pit.T.pick_f, Pit.T.submit_f, Pit.T.check_fail,
                    Pit.T.check_pass):
            self.track.append(f'{base} by:{by}')
        elif info in (Pit.T.shift, Pit.T.cascade):
            self.track.append(f'{base} by:{by} from:{self.due}')
        elif info == Pit.T.extend:
            self.track.append(f'{base} from:{self.due}')
        else:
            self.track.append(base)

    def __json__(self):
        return {
            'id': self.id,
            'role_id': self.role_id,
            'dep': self.role.dep,
            'role': self.role.name,
            'pink_id': self.pink_id,
            'status': self.status,
            'start_at': self.start_at,
            'finish_at': self.finish_at,
            'due': self.due
        }
