import os
from unittest import TestCase, main
import datetime as dt
import time
from autofit.config import configuration
import autofit.models as m
import autofit.network as n
import autofit.proxy as p


class TestSlot(TestCase):

    @classmethod
    def setUpClass(cls):
        m.create_all(configuration['testing'])

    @classmethod
    def tearDownClass(cls):
        os.remove(configuration['testing'].DB_PATH)

    def test_start_producer(self):
        session = m.get_session()
        keys = '1|EUR|euro|equity|index'
        p1 = m.Producer(state=m.ProducerStatesEnum.completed, pname='totem_daily', keys=keys,
                        date=dt.datetime(2019, 6, 9).date(), args='{}')
        s1 = m.Slot(name='european_totem', keys=keys, date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        s2 = m.Slot(name='varswap_totem', keys=keys, date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        s3 = m.Slot(name='implied_vol', keys=keys, date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        s4 = m.Slot(name='dividends', keys=keys, date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        s5 = m.Slot(name='product_rate', keys=keys, date=dt.datetime(2019, 6, 9).date(),
                    priority=1, dbid='.')
        m.insert_slot(s1, p1)
        m.insert_slot(s2, p1)
        m.insert_slot(s3, p1)
        m.insert_slot(s4, p1)
        m.insert_slot(s5, p1)
        p.schedule_producers()
        for row in session.query(m.Producer):
            print row
        p.start_producers()
        time.sleep(5)
        p.start_producers()
        time.sleep(5)
        p.start_producers()


if __name__ == '__main__':
    main()