"""

"""

import logging
import requests
from autofit.parcels import ProducerInputs
import autofit.app.settings as settings

logger = logging.getLogger(__name__)
uri = 'http://localhost:5004/api/cal/execute/'


def execute(producers):
    input_ = ProducerInputs(server=settings.FLASK_SERVER_NAME, producers=producers)
    for producer in producers:
        logger.debug("Producer '%s' with pid '%s'" % (producer.pname, producer.pid))
        producer.running.set()
    request = requests.post(uri, json=input_)
    logger.debug("POST request return status_code %s" % request.status_code)
    if request.status_code == 200:
        for producer in producers:
            logger.debug("Producer with pid='%s' was ACCEPTED" % producer.pid)
    else:
        for producer in producers:
            logger.debug("Producer with pid='%s' was REJECTED" % producer.pid)
            producer.rejected.set()
        logger.exception("execution requests FAILED with status_code %s" % request.status_code)


