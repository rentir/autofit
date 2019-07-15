"""

"""

import datetime
import json
import autofit.network as network
from autofit.utils import import_from_package


class ProducerException(Exception):
    pass


class RequiredSlot(object):

    def __init__(self, slot_name, filter_, exclusive=False):
        self.slot_name = slot_name
        self.filter = filter_
        self.exclusive = exclusive


class _ProducerBase(object):

    def __init__(self, name, requires, provides, priority, filters, delay, batch_size, exclusive):
        self.name = name
        self.requires = requires if requires else []
        self.provides = provides
        self.priority = priority
        self.filters = filters
        self.delay = delay
        self.batch_size = batch_size or 1
        if self.batch_size < 1:
            raise ProducerException("Producer %s: batch_size must be positive" % name)
        self.exclusive = (exclusive is not None and exclusive)
        network.link_producer(self)

    @property
    def keys(self):
        outslot = self.provides[0]
        return outslot.keys.split('|')


class Daemon(_ProducerBase):

    def __init__(self, name, provides):
        super(Daemon, self).__init__(name=name, requires=None, provides=provides, priority=0,
                                     filters={}, delay=0, batch_size=None, exclusive=False)


class Producer(_ProducerBase):

    def __init__(self, name, requires, provides, priority, filters=None, delay=None, batch_size=None, exclusive=True):
        super(Producer, self).__init__(name=name, requires=requires, provides=provides, priority=priority,
                                       filters=filters or [], batch_size=batch_size, delay=delay or 0,
                                       exclusive=exclusive)


class JoinedSlot(object):
    def __init__(self, slot, alias=None, slot_keys=None, producer_keys=None, exclusive=False):
        self.name = slot
        self.alias = alias
        if bool(slot_keys) ^ bool(producer_keys):
            raise ProducerException("Either both keys are passed or none")
        if slot_keys:
            self.slot_keys = slot_keys
            self.producer_keys = producer_keys
        else:
            self.slot_keys = self.producer_keys = None
        self.exclusive = exclusive


class _Slot(dict):
    def __init__(self, sname, keys, dbid):
        super(_Slot, self).__init__(sname=sname, keys=keys, dbid=dbid)


class Parcel(dict):
    def __init__(self, pname, pid, date, slots, state, priority):
        super(Parcel, self).__init__(pname=pname, pid=pid, date=date,
                                     slots=slots, state=state, priority=priority)

    @classmethod
    def decode(cls, content):
        return cls(pname=content['pname'], pid=content['pid'],
                   date=datetime.datetime.strptime(content['date'], '%Y-%m-%d').date(),
                   slots=content['slots'], state=content['state'], priority=content['priority'])


import_from_package(__file__, __package__)


