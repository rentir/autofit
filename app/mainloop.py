"""

"""

from threading import Thread
from Queue import Queue
import time
import logging
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import autofit.network as net
from autofit.models import Producer, get_session, Slot, insert_slot, ProducerStatesEnum, SlotStatesEnum
from autofit.producers import Daemon
from autofit.proxy import schedule_producers, start_producers

logger = logging.getLogger(__name__)


class MainloopException(Exception):
    pass


class MainloopCorruptedProducer(MainloopException):
    pass


class Loop(Thread):
    """

    """
    def __init__(self, queue):
        self.queue = queue  # type: Queue
        super(Loop, self).__init__()
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        logger.debug("autofit.app.Loop STARTED!")
        session_ = get_session()
        while not self._stop:
            if self.queue.empty():
                time.sleep(2)
            else:
                parcel = self.queue.get()
                if parcel['state'] != 'ok':
                    continue
                pname = parcel['pname']
                pid = parcel['pid']
                logger.debug("Receiver data from producer with pid '%s'" % pid)
                if pid:
                    query = session_.query(Producer).filter_by(pid=pid)
                    try:
                        p = query.one()
                        if p.halted():
                            logger.debug("Producer with pid='%s' was halted, update skipped" % pid)
                            continue
                        if not p.running():
                            logger.error("Producer with pid='%s' in an inconsistent state '%s'" % (pid, p.state))
                            continue
                    except NoResultFound:
                        logger.exception("producer with pid='%s' does not exist" % pid)
                        continue
                    except MultipleResultsFound:
                        logger.exception("multiple producer with pid='%s'" % pid)
                        continue
                    except Exception as e:
                        logger.exception(str(e))
                elif not isinstance(net.producers[pname].obj, Daemon):
                    logger.exception("non-daemon producer missing pid")
                else:  # the producer is a daemon, set p to None
                    p = None
                logger.debug("valid data received from pid='%s'" % pid)
                date = parcel['date']
                priority = parcel['priority']
                if p:
                    p.completed.set()
                    for slot in p.inputs:
                        is_completed = True
                        for producer in slot.listeners:
                            if not producer.completed():
                                is_completed = False
                                break
                        if is_completed:
                            slot.current.set()
                for slot in parcel['slots']:
                    oslot = Slot(name=slot['sname'], keys=slot['keys'], date=date, priority=priority,
                                 state=SlotStatesEnum.pending, dbid=slot['dbid'])
                    insert_slot(oslot, p)
            schedule_producers()
            start_producers()
        logger.debug('mail loop halted')
