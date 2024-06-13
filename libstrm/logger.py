import logging
from logging import Formatter
from logging import Filter
from multiprocessing import Queue
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler

__all__ = ['log_queue', 'info', 'error', 'warning', 'debug', 'critical', 'exception', 'fatal', 'set_file', 'set_queue', 'set_stream', 'log_listener', 'start', 'stop']

level=logging.INFO
_logger = logging.getLogger()
_logger.setLevel(level)
log_queue = Queue()
listener = None
fmt = Formatter('%(asctime)s [%(levelname)-7s] [P%(process)6d|T%(thread)6d] %(module)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class LogFilter(Filter):
    def filter(self, record):
        if record.module == '_client':
            return False
        return True
    
log_filter = LogFilter("httpx_client")

_logger.addFilter(log_filter)

def info(msg, *args, **kwargs):
    _logger.info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    _logger.error(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    _logger.warning(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    _logger.debug(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    _logger.critical(msg, *args, **kwargs)

def exception(msg, *args, **kwargs):
    _logger.exception(msg, *args, **kwargs)

def fatal(msg, *args, **kwargs):
    _logger.fatal(msg, *args, **kwargs)

def set_file(path="xiaoya_strm.log", **kwargs):
    kwargs = {**{'maxBytes': 1024*1024*100, 'backupCount': 1, 'encoding': 'utf-8'}, **kwargs}
    handler = RotatingFileHandler(path, **kwargs)
    handler.setLevel(level)
    handler.setFormatter(fmt)
    handler.addFilter(log_filter)
    _logger.addHandler(handler)

def set_queue(queue = None):
    handler = QueueHandler(queue or log_queue)
    handler.setLevel(level)
    # handler.setFormatter(fmt)
    _logger.addHandler(handler)

def set_stream():
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(fmt)
    handler.addFilter(log_filter)
    _logger.addHandler(handler)

def start_listener(_queue = None):
    global listener
    listener = QueueListener(_queue or log_queue, _logger)
    listener.start()

def setup_logging(log_filename = "xiaoya_strm.log", **kwargs):
    # set_queue()
    set_stream()
    set_file(log_filename, **kwargs)
    start_listener()

def stop():
    if listener:
        listener.stop()
    logging.shutdown()