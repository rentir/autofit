import os
from unittest import TestCase, main
import datetime as dt
from autofit.config import configuration
import autofit.models as m


class TestSlot(TestCase):

    @classmethod
    def setUpClass(cls):
        m.create_all(configuration['testing'])

    @classmethod
    def tearDownClass(cls):
        os.remove(configuration['testing'].DB_PATH)

    def test_slot_creation(self):
        session = m.get_session()
        s1 = m.Slot(sid='a', name='test_slot', keys='k1|k2', date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        s2 = m.Slot(sid='b', name='implied_volatilty', keys='k1|k2', date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.', state=m.SlotStatesEnum.current)
        p1 = m.Producer(state=m.ProducerStatesEnum.completed, pname='trs_fitter', keys='k1|k2',
                        date=dt.datetime(2019, 6, 9).date(), args='{}')
        s1.listeners.append(p1)
        p1.outputs.append(s2)
        session.add(s1)
        session.add(s2)
        session.add(p1)
        session.commit()
        session.query(m.Slot).filter_by(sid='a').one()
        session.query(m.Slot).filter_by(sid='b').one()
        session.query(m.Producer).one()

    def test_slot_insertion(self):
        session = m.get_session()
        s1 = m.Slot(name='european_totem', keys='k1|k2', date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        m.insert_slot(s1)
        s2 = m.Slot(name='varswap_totem', keys='k1|k2', date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        m.insert_slot(s2, None)
        for item in session.query(m.InputSlot):
            print item


if __name__ == '__main__':
    main()
