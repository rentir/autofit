import logging
import json
from flask import request
from flask_restplus import Resource
from autofit import queue
from autofit.producers import Parcel
from autofit.app.restplus import api

log = logging.getLogger(__name__)

ns = api.namespace('mrpr/results', description="Communication of producer's result")


@ns.route('/')
class Result(Resource):

    def get(self):
        return "Hello!"

    @api.response(201, 'Result successfully processed')
    # @api.expect(result)
    def post(self):
        """

        """
        data = json.loads(request.data)
        for content in data:
            queue.put(Parcel.decode(content))
        return None, 201
