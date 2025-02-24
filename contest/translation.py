from modeltranslation.translator import translator, TranslationOptions
from .models import Contest

class ContestTranslationOptions(TranslationOptions):
    fields = ('name', 'playing_desc', 'text_above_submit_button', 'text_after_submit', 'text_instead_of_date')

translator.register(Contest, ContestTranslationOptions)
