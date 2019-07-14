"""

"""
import logging


logger = logging.getLogger(__name__)
producers = {}
slots = {}
daemons = {}
_unlinked_requires = {}
_unlinked_provides = {}


class IncompleteNetwork(Exception):
    pass


class SlotNode(object):
    def __init__(self, obj):
        self.obj = obj
        self.producers = set()
        self.listeners = set()

    def __repr__(self):
        return "<SlotNode(obj=%s, producers=%s, listeners=%s)>" % (self.obj, self.producers, self.listeners)


class ProducerNode(object):
    def __init__(self, obj):
        self.obj = obj
        self.provides = set()
        self.requires = set()

    def __repr__(self):
        return "<ProducerNode(obj=%s, provides=%s, requires=%s)>" % (self.obj, self.provides, self.requires)


def link_slot(slot):
    logger.debug("linking slot '%s'" % slot.name)
    if slot.name in slots:
        raise Exception("slot '%s' was already linked" % slot.name)
    node = SlotNode(slot)
    slots[slot.name] = node
    # This is a new slots, check if it links to some of the unlinked producers
    for producer in _unlinked_requires:
        linked = set()
        if slot.name in _unlinked_requires[producer]:
            producers[producer.name].requires.add(node)
            linked.add(slot.name)
        if linked:
            _unlinked_requires[producer] -= linked
            if len(_unlinked_requires[producer]) == 0:
                del _unlinked_requires[producer]
    for producer in _unlinked_provides:
        linked = set()
        if slot.name in _unlinked_provides[producer]:
            producers[producer.name].requires.add(node)
            linked.add(slot.name)
        if linked:
            _unlinked_provides[producer] -= linked
            print len(_unlinked_provides[producer])
            if len(_unlinked_provides[producer]) == 0:
                del _unlinked_provides[producer]


def link_producer(producer):
    logger.debug("linking producer '%s'" % producer.name)
    if producer.name in producers:
        raise Exception("producer '%s' was already linked" % producer.name)
    unlinked_requires = set()
    unlinked_provides = set()
    node = ProducerNode(producer)
    producers[producer.name] = node
    for slot in producer.provides:
        if slot in slots:
            slots[slot].producers.add(node)
            node.provides.add(slots[slot])
        else:
            unlinked_provides.add(slot)
    if len(unlinked_provides) > 0:
        _unlinked_requires[producer.name] = unlinked_provides
    if len(producer.requires):
        for joined_slot in producer.requires:
            if joined_slot.name in slots:
                node.requires.add(slots[joined_slot.name])
                slots[joined_slot.name].listeners.add(node)
            else:
                unlinked_requires.add(joined_slot.name)
        if len(unlinked_requires) > 0:
            _unlinked_requires[producer.name] = unlinked_requires
    else:
        daemons[producer.name] = node


def is_fully_linked():
    return len(_unlinked_provides) == 0 and len(_unlinked_requires) == 0
