import enum

from sqlalchemy_ import (BaseModel, Column, ForeignKey, UniqueConstraint, hybrid_property,
                         relationship)
from sqlalchemy_.types import ARRAY, DateTime, Enum, String

__all__ = ['Pit']


class Pit(BaseModel):
    __tablename__ = 'pit'

    class State(enum.Enum):
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
    state = Column(Enum(State), default=State.init, index=True)
    track = Column(ARRAY(String), default=list)
    start_at = Column(DateTime)
    finish_at = Column(DateTime)
    due = Column(DateTime)
    timestamp = Column(DateTime)

    pink = relationship('Pink', back_populates='pits')
    role = relationship('Role', back_populates='pits')
    mangos = relationship('Mango',
                          back_populates='pit',
                          order_by='Mango.ver.desc()',
                          lazy='dynamic',
                          passive_deletes=True)
    __table_args__ = (UniqueConstraint('role_id', 'pink_id', name='_pit_uc'), )
    __id_len__ = 13

    class Trace(enum.Enum):
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

    def add_track(self, info: 'Pit.Trace', now, by=''):
        base = f'{info.value} - {now}'
        if info in (Trace.past_due, Trace.pick_f, Trace.submit_f, Trace.check_fail,
                    Trace.check_pass):
            self.track.append(f'{base} by:{by}')
        elif info in (Trace.shift, Trace.cascade):
            self.track.append(f'{base} by:{by} from:{self.due}')
        elif info == Trace.extend:
            self.track.append(f'{base} from:{self.due}')
        else:
            self.track.append(base)
