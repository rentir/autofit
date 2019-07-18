import datetime
import autofit.app.settings as settings
from autofit.models import Producer


# class SlotDict(dict):
#     """
#     The Slot representation as dict
#     """
#     def __init__(self, sname, keys, dbid):
#         """
#
#         :param sname: the slot's name
#         :type sname: str
#         :param keys: the string representing the slot's keys
#         :type keys: str
#         :param dbid: the id of the slot's data in the results database
#         :type dbid: str
#         """
#         super(SlotDict, self).__init__(sname=sname, keys=keys, dbid=dbid)


class ProducerOutput(dict):

    def __init__(self, content):
        super(ProducerOutput, self).__init__(pname=content['pname'], pid=content['pid'],
                                             date=datetime.datetime.strptime(content['date'], '%Y-%m-%d').date(),
                                             slots=content['slots'], state=content['state'],
                                             priority=content['priority'])

    @property
    def pname(self):
        return self['pname']

    @property
    def pid(self):
        return self['pid']

    @property
    def date(self):
        return self['date']

    @property
    def slots(self):
        return self['slots']

    @property
    def state(self):
        return self['state']

    @property
    def priority(self):
        return self['priority']


class ProducerOutputs(list):

    def __init__(self, content):
        super(ProducerOutputs, self).__init__([ProducerOutput(item) for item in content])


class ProducerInput(dict):
    def __init__(self, producer):
        """

        :param producer: the producer ORM object
        :type producer: Producer
        """
        content = producer._asdict()
        content['date'] = content['date'].strftime('%Y-%m-%d')
        content['last_updated'] = content['last_updated'].strftime('%Y-%m-%d %H-%M-%S')
        super(ProducerInput, self).__init__(content)


class ProducerInputs(dict):
    def __init__(self, server, producers):
        """

        :param server: the server posting the valuation request
        :type server: str
        :param producers: list of producers to be executed
        :type producers: list[Producer]
        """
        super(ProducerInputs, self).__init__(server=server or settings.FLASK_SERVER_NAME,
                                             data=[ProducerInput(producer) for producer in producers])

    @property
    def server(self):
        return self['server']

    @property
    def data(self):
        return self['data']

    def __iter__(self):
        return iter(self.data)
