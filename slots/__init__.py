"""

"""

import autofit.network as network
from autofit.utils import import_from_package


class _SlotBase(object):

    def __init__(self, name, keys=None, exclusive=False):
        keys = keys or 'id1|ccy1|id2|ccy2|class_|type_|currency|region'
        self.name = name
        self.keys = keys
        self.type_ = self.__class__.__name__.lower()
        self.exclusive = exclusive
        network.link_slot(self)


class MarketData(_SlotBase):

    def __init__(self, product, provider, keys=None):
        self._product = product
        self._provider = provider
        super(MarketData, self).__init__("%s_%s" % (product.lower(), provider.lower()), keys)

    def __repr__(self):
        return "<MarketData(product='%s', provider='%s', keys='%s')>" % (self._product, self._provider, self.keys)


class Parameter(_SlotBase):
    def __init__(self, input_, keys):
        super(Parameter, self).__init__(input_, keys)

    def __repr__(self):
        return "<Parameter(input_='%s', keys='%s')>" % (self.name, self.keys)


class Report(_SlotBase):
    def __init__(self, title, keys):
        super(Report, self).__init__(title, keys)

    def __repr__(self):
        return "<Report(title='%s', keys='%s')>" % (self.name, self.keys)


class Risk(_SlotBase):
    def __init__(self, greek, keys):
        super(Risk, self).__init__(greek, keys)

    def __repr__(self):
        return "<Risk(greek='%s')>" % (self.name, )


import_from_package(__file__, __package__)
