import enum

from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import ARRAY, Enum, DateTime, String

__all__ = ['Pit']


class Pit(BaseModel):
    __tablename__ = 'pit'

    # State
    class S(enum.Enum):
        init = 'initialized'
        pending = 'pending'
        working = 'working'
        delayed = 'delayed'
        past_due = 'past due'
        auditing = 'auditing'
        fin = 'finished'
        fin_p = 'finished (past due)'
        droped = 'droped'

    id = Column(String, primary_key=True)
    role_id = Column(String, ForeignKey('role.id', ondelete='CASCADE'))
    pink_id = Column(String, ForeignKey('pink.id', ondelete='SET NULL'))
    state = Column(Enum(S, name='pit_state'), default=S.init, index=True)
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

    # Trace
    class T(enum.Enum):
        pick_f = 'P'
        drop = 'd'
        shift = '<-'
        cascade = '->'
        past_due = '<>'
        submit = 's'
        submit_f = 'S'
        redo = 'r'
        check_pass = 'o'
        check_fail = 'x'
        extend = '+'

    def add_track(self, info: 'Pit.T', now, by=''):
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
