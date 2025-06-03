from functools import wraps
from logger import log_error

def catch_errors(func):
    """
    Decorator that catches and logs exceptions in any function.
    Logs specific OCR-related errors using FR06-level messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            log_error(f"[FR06] File not found: {str(e)}")
        except ValueError as e:
            log_error(f"[FR06] Value error: {str(e)}")
        except Exception as e:
            log_error(f"[FR06] Unexpected error in {func.__name__}: {str(e)}")
    return wrapper
