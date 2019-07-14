import logging

from flask_restplus import Resource
from autofit.app.restplus import api
from autofit.app.api.mrpr.serializers import inputslot
from autofit.models import InputSlot, get_session
from autofit.app.api.mrpr.business import get_inputslot, get_inputslots


log = logging.getLogger(__name__)

ns = api.namespace('mrpr/inputslots', description="Communication of input slots joining table")


@ns.route('/')
class InputSlotCollection(Resource):

    @api.marshal_list_with(inputslot)
    def get(self):
        return get_inputslots()


@ns.route('/<string:id>')
@api.response(404, 'Slot not found.')
class SlotItem(Resource):

    @api.marshal_with(inputslot)
    def get(self, id):
        """Returns details of a category."""
        return get_inputslot(id)






