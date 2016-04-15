from django.contrib.auth.decorators import login_required, user_passes_test, REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect


def somebody_only(function=None, redirect_field_name=None, case=None):
    CONDITIONS = {
        'anonymous': 'not request.user.is_authenticated()',
        'admin': 'request.user.is_authenticated() and request.user.is_staff',
        'user': 'request.user.is_authenticated() and not request.user.is_staff',
    }

    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if eval(CONDITIONS[case]):
                return view_func(request, *args, **kwargs)
            else:
                if eval(CONDITIONS['admin']) and request.path == '/home/':
                    return redirect('admin:index')
                if redirect_field_name and redirect_field_name in request.POST:
                    return HttpResponseRedirect(request.POST[redirect_field_name])
                raise Http404
        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__
        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


def admin_only(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    return somebody_only(function, redirect_field_name, 'admin')


def anonymous_only(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    return somebody_only(function, redirect_field_name, 'anonymous')


def user_only(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    return somebody_only(function, redirect_field_name, 'user')


# source: http://stackoverflow.com/questions/2307926/is-it-possible-to-decorate-include-in-django-urls-with-login-required
def required(wrapping_functions, patterns_rslt):
    """
    Used to require 1..n decorators in any view returned by a url tree

    Usage:
      urlpatterns = required(func,patterns(...))
      urlpatterns = required((func,func,func),patterns(...))

    Note:
      Use functools.partial to pass keyword params to the required
      decorators. If you need to pass args you will have to write a
      wrapper function.

    Example:
      from functools import partial

      urlpatterns = required(
          partial(login_required,login_url='/accounts/login/'),
          patterns(...)
      )
    """
    if not hasattr(wrapping_functions, '__iter__'):
        wrapping_functions = (wrapping_functions,)

    return [
        _wrap_instance__resolve(wrapping_functions, instance)
        for instance in patterns_rslt
    ]


# source: http://stackoverflow.com/questions/2307926/is-it-possible-to-decorate-include-in-django-urls-with-login-required
def _wrap_instance__resolve(wrapping_functions, instance):
    if not hasattr(instance, 'resolve'):
        return instance
    resolve = getattr(instance, 'resolve')

    def _wrap_func_in_returned_resolver_match(*args, **kwargs):
        rslt = resolve(*args, **kwargs)
        if not hasattr(rslt, 'func'):
            return rslt
        f = getattr(rslt, 'func')
        for _f in reversed(wrapping_functions):
            f = _f(f)  # @decorate the function from inner to outer
        setattr(rslt, 'func', f)
        return rslt

    setattr(instance, 'resolve', _wrap_func_in_returned_resolver_match)
    return instance
