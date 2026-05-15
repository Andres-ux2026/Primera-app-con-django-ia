from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles:
                messages.error(request, 'No tienes permiso para acceder a esta página.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def student_required(view_func):
    return role_required('student')(view_func)


def teacher_required(view_func):
    return role_required('teacher', 'admin')(view_func)


def admin_required(view_func):
    return role_required('admin')(view_func)
