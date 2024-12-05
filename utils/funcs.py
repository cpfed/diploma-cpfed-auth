from django.http import HttpResponse
from django.utils.http import urlencode


def get_next_urlenc(request: HttpResponse):
    next_url = request.GET.get('next', '')
    return '?' + urlencode({'next': next_url}) if next_url else ''
