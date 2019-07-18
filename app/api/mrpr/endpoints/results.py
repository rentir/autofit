import logging
import json
from flask import request
from flask_restplus import Resource
from autofit import queue
from autofit.producers import Parcel
from autofit.app.restplus import api
from autofit.parcels import ProducerOutputs


log = logging.getLogger(__name__)

ns = api.namespace('mrpr/results', description="Communication of producer's result")


@ns.route('/')
class Result(Resource):

    @api.response(201, 'Result successfully processed')
    def post(self):
        """

        """
        data = json.loads(request.data)
        for content in ProducerOutputs(data):
            queue.put(content)
        return None, 201
