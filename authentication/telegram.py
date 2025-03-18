from django.conf import settings


def telegram_context_processor(request):
    return {
        "TELEGRAM_BOT_NAME": settings.TELEGRAM_BOT_NAME,
        "TELEGRAM_WEBHOOK_DOMAIN": settings.TELEGRAM_WEBHOOK_DOMAIN,
    }