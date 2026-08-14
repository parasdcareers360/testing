from functools import wraps
from logging_decorator import function_logger


# fixed retries
def retry(func, retries=3):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempts in range(retries):    
            try:
                return func(*args, **kwargs)
            except Exception:
                print("Exception Occurred %s", retries-attempts)
                if attempts == retries-1:
                    raise
    return wrapper

# configurable decorator
def retry_(retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempts in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    print("Exception Occurred %s", retries-attempts)
                    if attempts == retries-1:
                        raise
        return wrapper
    return decorator