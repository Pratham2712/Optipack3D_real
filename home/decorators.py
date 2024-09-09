from django.shortcuts import redirect
from django.conf import settings  # To use LOGIN_URL from settings

def custom_login_required(view_func=None, login_url=None):
    if not login_url:
        login_url = settings.LOGIN_URL  # Default to LOGIN_URL in settings if not provided

    def _decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Redirect to the login page
                return redirect('login')
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view

    if view_func:
        return _decorator(view_func)
    return _decorator
