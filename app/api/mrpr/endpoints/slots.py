"""

"""


import logging

from flask import request
from flask_restplus import Resource
from autofit.app.api.mrpr.serializers import slot
from autofit.app.restplus import api
from autofit.models import Slot, get_session
from autofit.app.api.mrpr.business import get_slots, get_slot

logger = logging.getLogger(__name__)

ns = api.namespace('mrpr/slots', description='Operations related to slots')


@ns.route('/')
class SlotsCollection(Resource):

    @api.marshal_list_with(slot)
    def get(self):
        """
        Returns list of blog categories.
        """
        return get_slots()


@ns.route('/<string:sid>')
@api.response(404, 'Slot not found.')
class SlotItem(Resource):

    @api.marshal_with(slot)
    def get(self, sid):
        """Returns details of a category."""
        return get_slot(sid)



