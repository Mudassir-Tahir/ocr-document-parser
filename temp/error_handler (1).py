from functools import wraps
from logger import log_error, log_info

def catch_errors(func):
    """
    Decorator that catches and logs exceptions in any function.
    Handles known project-level issues like:
    - File not found
    - Unreadable documents
    - Unknown document types
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            log_error(f"[FR06] File not found: {str(e)}")
            print("Error: The specified file was not found.")
        except ValueError as e:
            log_error(f"[FR06] Value error: {str(e)}")
            print("Error: Failed to process the input. Check format or content.")
        except Exception as e:
            log_error(f"[FR06] Unexpected error in {func.__name__}: {str(e)}")
            print("An unexpected error occurred during processing.")
    return wrapper
