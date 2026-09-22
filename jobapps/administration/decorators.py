from functools import wraps
from django.shortcuts import redirect


def administrator_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('administration:login')

        if request.user.base_role != 'ADMIN':
            return redirect('administration:login')

        return view_func(request, *args, **kwargs)

    return wrapper