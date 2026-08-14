import logging
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def function_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info("Started %s | args=%s | kwargs=%s", func.__name__, args, kwargs)

        try:
            result = func(*args, **kwargs)
            logging.info("Finished %s", func.__name__)
            return result
        except Exception:
            logging.exception("Error in %s", func.__name__)
            raise

    return wrapper
