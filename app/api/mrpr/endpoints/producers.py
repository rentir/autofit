"""

"""


import logging
from flask_restplus import Resource
from autofit.app.api.mrpr.serializers import producer
from autofit.app.restplus import api
from autofit.app.api.mrpr.business import get_producers, get_producer

logger = logging.getLogger(__name__)

ns = api.namespace('mrpr/producers', description='Operations related to producers')


@ns.route('/')
class ProducerCollection(Resource):

    @api.marshal_list_with(producer)
    def get(self):
        """
        Returns list of blog categories.
        """
        return get_producers()


@ns.route('/<string:pid>')
@api.response(404, 'Slot not found.')
class ProducerItem(Resource):

    @api.marshal_with(producer)
    def get(self, pid):
        """Returns details of a category."""
        return get_producer(pid)



