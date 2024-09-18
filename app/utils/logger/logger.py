import logging
import sys
from pythonjsonlogger import jsonlogger


class Logger:
    _instance = None
    app_logger = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, *args, **kwargs):
        facility = "kodee-demo"
        self.app_logger = logging.getLogger(facility)
        self.app_logger.setLevel(logging.INFO)
        self.app_logger.propagate = False

        if not any(isinstance(handler, logging.StreamHandler) for handler in self.app_logger.handlers):
            stream_handler = logging.StreamHandler(sys.stdout)
            formatter = jsonlogger.JsonFormatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
                json_ensure_ascii=False,
            )
            stream_handler.setFormatter(formatter)
            self.app_logger.addHandler(stream_handler)

    def log(self, message, level=logging.INFO, **kwargs):
        try:
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}

            log_methods = {
                logging.DEBUG: self.app_logger.debug,
                logging.INFO: self.app_logger.info,
                logging.WARNING: self.app_logger.warning,
                logging.ERROR: self.app_logger.error,
                logging.CRITICAL: self.app_logger.critical,
            }
            log_method = log_methods.get(level, self.app_logger.info)

            log_method(message, extra=filtered_kwargs)
        except Exception as e:
            print(f"Error while logging message: {e}")
