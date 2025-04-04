from django.http import JsonResponse

def health_check(request):
    """
    Basic health check endpoint for Kubernetes probes
    """
    return JsonResponse({"status": "ok"}, status=200) 