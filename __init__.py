"""

"""

import logging
from Queue import Queue
from importlib import import_module
import autofit.network as network
import autofit.models as models
import autofit.config as config


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
fhandler = logging.FileHandler('file.log')
fhandler.setFormatter(formatter)
fhandler.setLevel(logging.DEBUG)
logger.addHandler(fhandler)


# This will set up the producers/slots network
import_module('autofit.slots')
import_module('autofit.producers')


if not network.is_fully_linked():
    raise network.IncompleteNetwork("unlinked requires %s\nunliked provides %s" % (network._unlinked_requires,
                                                                                   network._unlinked_provides))
logger.info("Network was successfully linked")
models.create_all(config.Development)
logging.info("Database connected")
queue = Queue()
