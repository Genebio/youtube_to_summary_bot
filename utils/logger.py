import logging

LOGGER_FORMAT = "%(module)s | line %(lineno)-3d | %(levelname)-8s | %(message)s"

logger = logging.getLogger('shared_logger')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
logger.addHandler(handler)