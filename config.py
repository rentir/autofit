"""

"""

import os


class DbConfing(object):
    DB = 'sqlite:///'


class Development(DbConfing):
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db/mrprdev.db')


class Testing(DbConfing):
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests/mrprtest.db')


class Production(DbConfing):
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db/mrpr.db')


configuration = {'development': Development,
                 'testing': Testing,
                 'production': Production}
