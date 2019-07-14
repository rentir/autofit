"""

"""


from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from autofit import queue
import autofit.models as m


class BusinessException(Exception):
    """
    Base exception for the app.api.mrpr.business module
    """


def get_slots():
    session = m.get_session()
    return session.query(m.Slot).all()


def get_slot(sid):
    session = m.get_session()
    return session.query(m.Slot).filter_by(sid=sid).one()


def get_inputslots():
    session = m.get_session()
    return session.query(m.InputSlot).all()


def get_inputslot(id_):
    session = m.get_session()
    return session.query(m.InputSlot).filter_by(id_=id_).one()


def get_producers():
    session = m.get_session()
    return session.query(m.Producer).all()


def get_producer(pid):
    session = m.get_session()
    return session.query(m.Producer).filter_by(pid=pid).one()
