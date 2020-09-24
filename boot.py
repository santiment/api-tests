import logging
from api_tests.config import Config
from api_tests.constants import LOG_FORMAT, LOG_LEVEL, LOG_DATE_FORMAT, PYTHON_ENV

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt=LOG_DATE_FORMAT)
config = Config(PYTHON_ENV)
