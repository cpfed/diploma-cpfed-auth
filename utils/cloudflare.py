import requests
from cpfed.settings import CLOUDFLARE_SECRET_KEY, DEBUG
from django.core.exceptions import ValidationError


def check_turnstile_captcha(request):

    if DEBUG:
        return
    body = request.POST
    # Turnstile injects a token in "cf-turnstile-response".
    token = body.get('cf-turnstile-response')
    ip = request.META.get('HTTP_CF_CONNECTING_IP')

    # Validate the token by calling the "/siteverify" API.
    form_data = {
        'secret': CLOUDFLARE_SECRET_KEY,
        'response': token,
        'remoteip': ip
    }

    result = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=form_data)
    outcome = result.json()
    if not outcome.get('success'):
        raise ValidationError("The provided Turnstile token was not valid!")