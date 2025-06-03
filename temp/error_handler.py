from functools import wraps
from logger import log_error

def catch_errors(func):
    """
    Decorator to wrap functions and log any exceptions they raise.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(f"Exception in {func.__name__}: {str(e)}")
            return None
    return wrapper
