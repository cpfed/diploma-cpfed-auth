from django.views.decorators.csrf import csrf_exempt
import http
import json
import jwt

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from authentication.models import OnsiteLogin


@csrf_exempt
def oqylyk_get_token(request: HttpResponse):
    if request.method == 'POST':
        try:
            data = json.loads(str(request.body, encoding="utf-8"))
            handle = data.get('email', '')
            secret_code = data.get('password', '')
            jwt_token = jwt.encode({"handle": handle, "secret_code": secret_code}, settings.OQYLYK_JWT_SECRET,
                                   algorithm="HS256")
            return HttpResponse(jwt_token)
        except json.decoder.JSONDecodeError:
            pass
    return HttpResponse(status=http.HTTPStatus.BAD_REQUEST)
