import logging
from flask import Flask, Blueprint
from autofit import queue
from autofit.app import settings
from autofit.app.restplus import api
from autofit.app.api.mrpr.endpoints.results import ns as results_namespace
from autofit.app.api.mrpr.endpoints.slots import ns as slots_namespace
from autofit.app.api.mrpr.endpoints.inputslots import ns as inputslots_namespace
from autofit.app.api.mrpr.endpoints.producers import ns as producers_namespace
from autofit.app.mainloop import Loop

app = Flask(__name__)
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP


def initialize_app(flask_app):
    configure_app(flask_app)
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(results_namespace)
    api.add_namespace(slots_namespace)
    api.add_namespace(inputslots_namespace)
    api.add_namespace(producers_namespace)
    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(port=settings.FLASK_SERVER_PORT, debug=settings.FLASK_DEBUG, use_reloader=settings.FLASK_USE_RELOADER)


if __name__ == '__main__':
    loop = Loop(queue)
    loop.start()
    main()
