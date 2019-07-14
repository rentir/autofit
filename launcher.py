"""

"""

import logging
import requests
import autofit.app.settings as settings

logger = logging.getLogger(__name__)
uri = 'http://localhost:5001/api/cal/execute'


def execute(producer):
    content = {x.name: getattr(producer, x.name) for x in producer.__table__.columns}
    content['date'] = content['date'].strftime('%Y-%m-%d')
    content['last_updated'] = content['last_updated'].strftime('%Y-%m-%d')
    data = {'server': settings.FLASK_SERVER_NAME, 'data': content}
    logger.debug("executing producer with pid '%s'" % producer.pid)
    request = requests.post(uri, json=data)
    logger.debug("execution for pid '%s' executed with status %s'" % (producer.pid, request.status_code))
