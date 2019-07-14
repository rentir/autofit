import os
from glob import glob
from importlib import import_module
import inspect
import logging


logger = logging.getLogger(__name__)


class Singleton(type):
    def __init__(cls, name, bases, dic):
        super(Singleton,cls).__init__(name,bases,dic)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance=super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


def import_from_package(path, package):
    dirname = os.path.dirname(path)
    files = glob(os.path.join(dirname, '*.py'))
    logger.info('importing %s from %s' % (path, package))
    for f in files:
        name = inspect.getmodulename(f)
        if name != '__init__':
            logger.debug("importing module %s" % name)
            import_module('%s.%s' % (package, name))

