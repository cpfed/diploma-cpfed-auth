from modeltranslation.translator import translator, TranslationOptions
from .models import TelegramMessage


class TelegramMessageTranslationOptions(TranslationOptions):
    fields = ('data', )


translator.register(TelegramMessage, TelegramMessageTranslationOptions)
