import logging
import datetime as dt
import json
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, or_, and_, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy_fsm import FSMField, transition
from uuid import uuid4


logger = logging.getLogger(__name__)
Base = declarative_base()
database = {'engine': None,
            'session': None}

_uuid_generator = lambda: uuid4().get_hex()


class ModelException(Exception):
    pass


class InconsistentProducerState(ModelException):
    pass


class MultipleProducerException(ModelException):
    pass


class SlotStatesEnum(object):
    void = 'void'
    failed = 'failed'
    pending = 'pending'
    current = 'current'
    stale = 'stale'


class ProducerStatesEnum(object):
    void = 'void'
    scheduled = 'scheduled'
    pending = 'pending'
    running = 'running'
    completed = 'completed'
    halted = 'halted'
    failed = 'failed'
    rejected = 'rejected'


class InputSlotStatesEnum(object):
    updated = 'updated'
    processed = 'processed'


slot_producer_association = Table('slot_producer_association', Base.metadata,
                                  Column('slot_id', Integer, ForeignKey('slots.sid')),
                                  Column('producer_id', Integer, ForeignKey('producers.pid')))

producer_slot_association = Table('producer_slot_association', Base.metadata,
                                  Column('slot_id', Integer, ForeignKey('slots.sid')),
                                  Column('producer_id', Integer, ForeignKey('producers.pid')))


class DictMixin(object):
    def _asdict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Slot(Base):
    """
    :cvar sid: slot class id
    :type sid: int
    :cvar name: slot's name
    :type name: str
    :cvar keys: concatenation of columns of Underlying table, sorted alphanumerically and joined by |
    :type keys: str
    :cvar date: valuation date
    :type date: Date
    :cvar priority: slot's priority
    :type priority: int
    :cvar dbid: location of slot's data
    :type dbid: str
    """
    __tablename__ = 'slots'
    sid = Column(String, primary_key=True, default=_uuid_generator)
    name = Column(String, index=True)
    keys = Column(String)
    date = Column(Date, nullable=False, index=True)
    priority = Column(Integer)
    state = Column(FSMField, default=SlotStatesEnum.void, nullable=False)
    updated_at = Column(DateTime, default=dt.datetime.utcnow)
    dbid = Column(String, nullable=True)
    listeners = relationship("Producer", secondary=slot_producer_association, backref='inputs')

    @transition(source='*', target=SlotStatesEnum.pending)
    def pending(self):
        pass

    @transition(source=SlotStatesEnum.pending, target=SlotStatesEnum.current)
    def current(self):
        pass

    @transition(source=SlotStatesEnum.pending, target=SlotStatesEnum.failed)
    def failed(self):
        pass

    @transition(source=[SlotStatesEnum.current, SlotStatesEnum.pending, SlotStatesEnum.failed],
                target=SlotStatesEnum.stale)
    def stale(self):
        pass

    def __repr__(self):
        return "<Slot(sid=%s, name='%s', keys='%s', date=%s, priority=%s, state='%s', dbid='%s')>" % \
                (self.sid, self.name, self.keys, self.date, self.priority, self.state, self.dbid)


def invalidate_slot(slot):
    session_ = get_session()
    logger.debug("invalidating %s" % slot)
    for producer in slot.listeners:  # type: Producer
        for s in producer.outputs:
            invalidate_slot(s)
        if producer.running():
            producer.halted.set()
        for s in producer.outputs:  # we need to recursicely invalidate
            invalidate_slot(s)
        else:
            logger.debug("dangling product %s being removed" % producer)
            session_ = database['session']
            session_.delete(producer)
    session_.query(InputSlot).filter_by(sid=slot.sid).delete()
    slot.stale.set()


def insert_slot(slot, producer=None):
    from autofit.proxy import broadcast
    session_ = database['session']
    logger.debug("inserting slot %s" % slot.sid)
    q = session_.query(Slot).filter(and_(Slot.name == slot.name,
                                         Slot.keys == slot.keys,
                                         Slot.date == slot.date)).filter(or_(Slot.current(), Slot.pending()))
    try:
        slot0 = q.one()
        logger.debug("found existing current slot '%s'" % slot0.sid)
        if slot0.priority <= slot.priority:
            logger.debug("new slot has higher priority")
            invalidate_slot(slot0)
        else:
            logger.debug("new slot has lower priority, skipped")
            return False  # nothing to do, the new slot has priority lower than the current one
    except NoResultFound:
        logger.debug("The slot is NEW")
    except MultipleResultsFound:
        logger.error("db in inconsistent state, more than one slot found")
    except Exception as e:
        raise e
    if len(slot.listeners) == 0:
        slot.current.set()
    session_.add(slot)
    if producer:
        producer.outputs.append(slot)
    broadcast(slot)
    slot.pending.set()
    session_.commit()
    return True


class Underlying(Base):
    """
    :cvar uname: ubsid
    :type uname: str
    :cvar currency: denomination currency
    :type currency: str
    :cvar ric: Reuters code
    :type ric: str
    :cvar class_: asset class (equity, rate, fx)
    :type class_: str
    :cvar type_: Underlying type (Equity Stock, Equity Index etc...)
    :type type_: str
    :cvar region: Underlying's region (for example 'euro')
    :type region: str 
    """
    __tablename__ = 'underlyings'
    uname = Column(String, primary_key=True)
    currency = Column(String, index=True)
    ric = Column(String, nullable=True)
    class_ = Column(String)  # Underlying class
    type_ = Column(String)  # Underlying type (Equity Stock, Equity Index etc)
    region = Column(String)

    def __repr__(self):
        return "<Underlying(uname='%s', " \
               "currency='%s', " \
               "ric='%s', class_='%s', type_='%s',region='%s')>" % \
               (self.uname, self.currency, self.ric, 
                self.class_, self.type_, self.region)


class InputSlot(Base):
    """
    Joining table
    """
    __tablename__ = 'input_slots'
    id_ = Column(Integer, primary_key=True)
    pname = Column(String, index=True, nullable=False)
    sname = Column(String, index=True, nullable=False)
    sid = Column(String, index=True)
    id1 = Column(String, index=True, nullable=False)
    ccy1 = Column(String, index=True, nullable=True)
    id2 = Column(String, index=True, nullable=True)
    ccy2 = Column(String, index=True, nullable=True)
    class_ = Column(String, index=False, nullable=True)
    type_ = Column(String, index=False, nullable=True)
    region = Column(String, index=True, nullable=True)
    date = Column(Date, index=True)
    last_updated = Column(DateTime, default=dt.datetime.utcnow)
    state = Column(FSMField, default=InputSlotStatesEnum.updated)

    @transition(source=InputSlotStatesEnum.updated, target=InputSlotStatesEnum.processed)
    def processed(self):
        pass

    @transition(source='*', target=InputSlotStatesEnum.updated)
    def updated(self):
        pass

    def __repr__(self):
        return "<InputSlot(id_=%s, pname='%s', sname='%s', sid='%s', " \
               "id1='%s', ccy1='%s', id2='%s', ccy2='%s', " \
               "class_='%s', type_='%s'', region='%s', " \
               "date=%s, last_updated=%s, state='%s'')" % (self.id_, self.pname, self.sname, self.sid, self.id1,
                                                           self.ccy1, self.id2, self.ccy2, self.class_, self.type_,
                                                           self.region, self.date, self.last_updated, self.state)


class Producer(Base, DictMixin):
    __tablename__ = 'producers'
    pid = Column(String, primary_key=True, index=True, nullable=False, default=_uuid_generator)
    pname = Column(String, index=True, nullable=False)
    keys = Column(String, index=True, nullable=False)
    args = Column(String, nullable=False)
    date = Column(Date, index=True, nullable=False)
    state = Column(FSMField, default=ProducerStatesEnum.void)
    last_updated = Column(DateTime, default=dt.datetime.utcnow)
    outputs = relationship("Slot", secondary=producer_slot_association, backref='producers')

    def __repr__(self):
        return "<Producer(pid='%s', pname='%s', keys='%s', " \
               "args='%s', date='%s', state='%s', last_updated='%s')>" % (self.pid, self.pname, self.keys, self.args,
                                                                          self.date, self.state, self.last_updated)

    @hybrid_property
    def delayed_by(self):
        return dt.datetime.utcnow() - self.last_updated

    @transition(source=ProducerStatesEnum.void, target=ProducerStatesEnum.scheduled)
    def scheduled(self):
        pass

    @transition(source=ProducerStatesEnum.void, target=ProducerStatesEnum.pending)
    def pending(self):
        pass

    @transition(source=[ProducerStatesEnum.pending,
                        ProducerStatesEnum.scheduled],
                target=ProducerStatesEnum.running)
    def running(self):
        pass

    @transition(source=ProducerStatesEnum.running, target=ProducerStatesEnum.completed)
    def completed(self):
        pass

    @transition(source=ProducerStatesEnum.running, target=ProducerStatesEnum.failed)
    def failed(self):
        pass

    @transition(source=ProducerStatesEnum.running, target=ProducerStatesEnum.halted)
    def halted(self):
        """
        Only if the state is 'running' then it will transact to 'halted'. In all other cases, the producer data can
        be updated
        """
        pass

    @transition(source=ProducerStatesEnum.pending, target=ProducerStatesEnum.rejected)
    def rejected(self):
        """
        The worker rejected the producer execution
        """
        pass


# to change to inster_producer(procer, slots)
def insert_producer(producer, slots):
    """
    pname, date, thiskeys, sids, args
    :param pkeys:
    :param args:
    :return:
    """
    from network import producers
    session_ = get_session()
    logger.info("Inserting producer '%s'" % producer.pname)
    query = session_.query(Producer).filter_by(pname=producer.pname, date=producer.date, keys=producer.keys)
    try:
        p = query.filter(Producer.running()).one()  # it is already running. stop it
        p.halted.set()
        logger.debug("One instance already running, it is halted now")
    except NoResultFound:  # it is not running
        pass
    except MultipleResultsFound:
        logger.exception("Multiple producer for same pid")
        raise MultipleProducerException()
    except Exception as e:
        logger.exception("exception %s" % str(e))
        raise e
    p = query.filter(or_(Producer.pending(), Producer.scheduled())).all()
    if len(p) == 0:  # uhm we need to insert it
        p = producer
        p.pending.set()
        logger.debug("Created new producer")
        session_.add(p)
    elif len(p) > 1:
        logger.exception("Found producer '%s' both 'pending' and 'scheduled'" % producer.pid)
        raise InconsistentProducerState("Found producer '%s' both 'pending' and 'scheduled'" % producer.pid)
    else:
        p = p[0]
    p.args = producer.args
    p.last_updated = dt.datetime.utcnow()
    for slot in slots:
        if p not in slot.listeners:
            slot.listeners.append(p)
            logger.debug("'%s' linked to '%s'" % (p.pid, slot.sid))
    logger.info("'%s' successfully inserted" % p.pid)


def create_all(conf):
    engine = create_engine(conf.DB + conf.DB_PATH)
    database['engine'] = engine
    session_factory = sessionmaker(bind=engine)
    database['session'] = scoped_session(session_factory)
    Base.metadata.create_all(engine)


def get_session():
    """

    :return: SQLAlchemy session
    :rtype: Session
    """
    if database['session']:
        return database['session']
    raise RuntimeError("session not initiated")


def get_engine():
    if database['engine']:
        return database['engine']
    raise RuntimeError("engine not initiated")


if __name__ == '__main__':
    import os
    import datetime as dt
    from config import configuration

    os.remove(os.path.join('db', 'mrb.db'))
    create_all(configuration['production'])
    session = get_session()
    s1 = Slot(name='european.totem', keys='k1|k2', date=dt.datetime(2019, 6, 9).date(),
              priority=1, path='.', state=SlotStatesEnum.current)
    p1 = Producer(state=ProducerStatesEnum.completed)
    s1.producers.append(p1)
    s2 = Slot(name='implied_volatilty', keys='k1|k2', date=dt.datetime(2019, 6, 9).date(),
              priority=1, path='.', state=SlotStatesEnum.current)
    p1.slots.append(s2)
    session.add(s1)
    session.add(p1)
    session.commit()
    s1n = Slot(name='european.totem', keys='k1|k2', date=dt.datetime(2019, 6, 9).date(),
               priority=2, path='.', state=SlotStatesEnum.void)
    session.add(s1n)
    insert_slot(s1n)
