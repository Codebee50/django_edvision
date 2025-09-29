from urllib.parse import urlparse
import time
import functools

def measure_time_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        return result
    return wrapper

def get_first_error(errors):
    """
    Gets the first message in a serializer.errors
    
    Parameters:
    errors: The error messages of a serializer i.e serializer.errors
    """
    field, error_list = next(iter(errors.items()))
    return str(error_list[0]) 

def format_first_error(errors, with_keys=True):
    field, error_list = next(iter(errors.items()))
    if isinstance(error_list, list):
        if isinstance(error_list[0], dict):
            return format_first_error(error_list[0])
        return f"{field} - {error_list[0]}" if with_keys else error_list[0]
    else:
        return format_first_error(error_list)
    


def get_request_origin(request):
    origin = request.META.get("HTTP_ORIGIN", None)
    print('the origin is', origin)
    referrer = request.META.get('HTTP_REFERER', origin)
    
    if referrer:
        parsed_url = urlparse(referrer)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return origin
    return "httpS://erdvision.dev"