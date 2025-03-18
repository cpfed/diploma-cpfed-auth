import functools

from django.http import HttpResponse
from django.utils.http import urlencode
from django.utils.crypto import get_random_string


def get_next_urlenc(request: HttpResponse):
    next_url = request.GET.get('next', '')
    return '?' + urlencode({'next': next_url}) if next_url else ''

def gen_unambiguous_random_string(n: int = 8):
    return get_random_string(n, "cdefhjkmnprtvwxy2345689")

def only_admin_view(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pass