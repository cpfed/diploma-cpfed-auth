from django import template
from django.urls import translate_url, reverse
from django.utils.translation import activate

register = template.Library()


@register.simple_tag(takes_context=True)
def change_lang(context, lang: str, *args, **kwargs):
    path = context['request'].path
    # return translate_url(path, lang)
    return f'/{lang}{path[3:]}'