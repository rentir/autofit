"""

"""

import logging
import requests
import autofit.app.settings as settings

logger = logging.getLogger(__name__)
uri = 'http://localhost:5001/api/cal/execute'


def execute(producers):
    data = {'server': settings.FLASK_SERVER_NAME, 'data': []}
    for producer in producers:
        content = {x.name: getattr(producer, x.name) for x in producer.__table__.columns}
        content['date'] = content['date'].strftime('%Y-%m-%d')
        content['last_updated'] = content['last_updated'].strftime('%Y-%m-%d')
        data['data'].append(content)
        logger.debug("adding task for producer with pid '%s'" % producer.pid)
        producer.running.set()
    request = requests.post(uri, json=data)
    n = len(producers)
    logger.debug("%s execution%s requested with status '%s'" % (n, 's' if n > 1 else '', request.status_code))
