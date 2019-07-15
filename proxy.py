"""
producer proxy
"""

import logging
import re
import json
import datetime as dt
from sqlalchemy import and_, select, cast, literal, String, alias, func
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import object_session, aliased
from autofit.models import InputSlot, get_session, MultipleProducerException, InconsistentProducerState
import autofit.network as net
from autofit.models import Slot, InputSlot, insert_producer, Producer, ProducerStatesEnum, InputSlotStatesEnum
import autofit.producers as ptypes
from autofit.launcher import execute


logger = logging.getLogger(__name__)
_broadcasting_slots = {}


class BroadcastingError(Exception):
    pass


def notify(slot, producer, callback):
    """

    :param slot: slot broadcasting the updated state
    :type slot:  Slot
    :param producer: the producer being notifies
    :type producer: Root or Producer
    :param callback: to acknowledge back the data was processed
    :type callback: func
    """
    session = object_session(slot)
    sname = slot.name
    slot_type = net.slots[sname].obj
    pname = producer.name
    # Here we need to filter
    if len(producer.filters):
        for key, filter_ in producer.filters.items():
            m = re.match(filter_, slot.__dict__[key], re.DOTALL)
            if not m:
                callback(producer, False)
    slot_keys = slot_type.keys.split('|')
    this_keys = slot.keys.split('|')
    keys_map = zip(slot_keys, this_keys)
    q = session.query(InputSlot).filter_by(sname=sname).filter_by(pname=pname).filter_by(date=slot.date)
    for k, v in keys_map:
        q = q.filter(InputSlot.__dict__[k] == v)
    try:
        ps = q.one()
        ps.sid = slot.sid
        logger.debug('InputSlot %s was updated' % ps)
    except MultipleResultsFound as e:
        logger.exception(str(e))
        raise e
    except NoResultFound:
        ps = InputSlot(sid=slot.sid, sname=sname, pname=pname, date=slot.date)
        for k, v in keys_map:
            ps.__dict__[k] = v
        session.add(ps)
        logger.debug('InputSlot %s was created' % ps)
    session.commit()
    callback(producer)


def broadcast(slot):
    if slot.name in _broadcasting_slots:
        raise BroadcastingError()
    affected = net.slots[slot.name].listeners
    _broadcasting_slots[slot.name] = len(affected)
    for producer in affected:
        logger.debug("broadcasting to '%s'" % producer.obj.name)
        notify(slot, producer.obj, acknowledge(slot))


def acknowledge(slot):
    """

    :param slot: the slot broadcasting the update
    :type slot: Slot
    :return: the acknowledging function
    :rtype: func
    """
    def inner(producer, result=True):
        _broadcasting_slots[slot.name] -= 1
        logger.debug("acknowledge received from '%s' with result '%s'" % (producer.name, result))
        logger.debug("pending %s acknowledgments" % _broadcasting_slots[slot.name])
        if _broadcasting_slots[slot.name] == 0:
            del _broadcasting_slots[slot.name]
            slot.pending.set()
    return inner


def schedule_producers():
    ids = set()
    session_ = get_session()
    potprods = session_.query(InputSlot.pname).filter(InputSlot.updated()).distinct()
    for producer in potprods:
        pname = producer.pname
        logger.debug("joining producer %s" % pname)
        oproducer = net.producers[pname].obj  # type: ptypes._ProducerBase
        skeys = net.slots[oproducer.provides[0]].obj.keys.split('|')
        spkeys = skeys + ['pname', 'date']
        fkeys = [InputSlot.__dict__[key] for key in spkeys]  # keys mapped to the ORM attributes
        ukeys = session_.query(*fkeys).filter(and_(InputSlot.updated(),
                                                   InputSlot.pname == pname))
        for fkey in fkeys:
            ukeys = ukeys.filter(fkey.isnot(None))  # TODO: do I really need this?
        ukeys = ukeys.group_by(*fkeys).distinct()
        for ukey in ukeys:
            date = ukey.date
            keys_dict = ukey._asdict()
            seed = alias(select([cast(literal(val), String).label(key) for key, val in keys_dict.items()]), 'seed')
            joins = []
            columns = []
            ons = []
            counter = {}
            sids = set()
            for jslot in oproducer.requires:  # type: ptypes.JoinedSlot
                name = jslot.alias or jslot.name
                if name in counter:
                    name_ = jslot.alias or "%s_%s" % (name, counter[name])
                    counter[name] += 1
                else:
                    name_ = name
                    counter[name] = 1
                table = session_.query(aliased(InputSlot, name=name_)).filter_by(sname=name,
                                                                                 pname=pname,
                                                                                 date=date).subquery()
                joins.append(table)
                this_column = table.c.sid.label(name_)
                columns.append(this_column)
                join_on = True
                slot_keys = jslot.slot_keys or skeys
                producer_keys = jslot.producer_keys or skeys
                for s, p in zip(slot_keys, producer_keys):
                    join_on = and_(join_on, seed.c[p] == table.c[s])
                for row in session_.query(table.c.sid).select_from(seed.join(table, join_on)):
                    # need to keep track of this to link the producer to the slots it processes
                    #
                    sids.add(row.sid)
                for row in (session_.query(table.c.id_).
                            select_from(seed.join(table, join_on)).
                            filter(table.c.state == InputSlotStatesEnum.updated)):
                    ids.add(row.id_)  # need to keep track of this to set the 'processed' state to used InputSlot
                    logger.debug('added id_ %s' % row.id_)
                ons.append(join_on)
            seed = session_.query(seed, *columns)
            for table, on, jslot in zip(joins, ons, oproducer.requires):
                if jslot.exclusive:
                   seed = seed.outerjoin(table, on).filter(table.c.id_.is_(None))
                else:
                    seed = seed.join(table, on)
            if seed.count():
                args = [row._asdict() for row in seed]
                args = json.dumps(args)
                slots = session_.query(Slot).filter(Slot.sid.in_(sids)).all()
                logger.debug("producer '%s' is READY" % pname)
                this_keys = '|'.join([keys_dict[k] for k in skeys])
                this_producer = Producer(state=ProducerStatesEnum.void, pname=pname,
                                         keys=this_keys, date=date, args=args)
                try:
                    insert_producer(producer=this_producer, slots=slots)
                except (InconsistentProducerState, MultipleProducerException) as e:
                    logger.exception(str(e))
                    continue  # some other action here
            else:
                logger.debug("producer '%s' is INCOMPLETE" % pname)
    for input_slot in session_.query(InputSlot).filter(InputSlot.id_.in_(ids)):
        logger.info("Setting InputSlot.state='processed' to InputSlot.id_='%s', "
                    "pname='%s', sname='%s', sid='%s'" % (input_slot.id_, input_slot.pname,
                                                          input_slot.sname, input_slot.sid))
        input_slot.processed.set()
    session_.commit()


def start_producers():
    session_ = get_session()
    pnames = [x[0] for x in session_.query(Producer.pname).filter(Producer.pending()).distinct()]
    for pname in pnames:
        pobj = net.producers[pname].obj
        batch_size = pobj.batch_size
        min_delay = dt.timedelta(seconds=pobj.delay)
        producers = (session_.query(Producer).filter(Producer.pending()).
                     filter(Producer.pname == pname).filter(Producer.delayed_by > min_delay))
        for idx in range(0, len(producers), batch_size):
            execute(producers[idx:(idx+batch_size)])
            for p in producers:
                p.running.set()
    session_.commit()
