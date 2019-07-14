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

    def __init__(self, name, requires, provides, priority, filters, delay, exclusive):
        self.name = name
        self.requires = requires if requires else []
        self.provides = provides
        self.priority = priority
        self.filters = filters
        self.delay = delay
        self.exclusive = exclusive
        network.link_producer(self)

    @property
    def keys(self):
        outslot = self.provides[0]
        return outslot.keys.split('|')


class Daemon(_ProducerBase):

    def __init__(self, name, provides):
        super(Daemon, self).__init__(name=name, requires=None, provides=provides, priority=0,
                                     filters={}, delay=0, exclusive=False)


class Producer(_ProducerBase):

    def __init__(self, name, requires, provides, priority, filters=None, delay=None, exclusive=True):
        super(Producer, self).__init__(name=name, requires=requires, provides=provides, priority=priority,
                                       filters=filters or [], delay=delay or 0, exclusive=exclusive)


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
        result = json.loads(content)
        return cls(pname=result['pname'], pid=result['pid'],
                   date=datetime.datetime.strptime(result['date'], '%Y-%m-%d').date(),
                   slots=result['slots'], state=result['state'], priority=result['priority'])


import_from_package(__file__, __package__)


