from functools import wraps
from django.contrib.auth import logout as auth_logout

def logout_after_10_minutes(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Set session expiration time to 10 minutes (600 seconds)
        request.session.set_expiry(6000)
        return view_func(request, *args, **kwargs)
    return wrapped_view

