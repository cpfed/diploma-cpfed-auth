from django.shortcuts import render
from django.http import HttpResponse, response, JsonResponse

from .models import Region

def api_regions(request: HttpResponse):
    regions = Region.objects.all().values_list('id', 'name')
    return JsonResponse({
        "count": len(regions),
        "next": 1,
        "previous": 1,
        "results": [{"id": r[0], "name": r[1]} for r in regions]
    })