import logging
from flask_restplus import Api
from autofit.app import settings


log = logging.getLogger(__name__)
api = Api(version='1.0', title='Autofit API',
          description='A simple demonstration of the Autofit IPV system')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)
    if not settings.FLASK_DEBUG:
        return {'message': message}, 500
