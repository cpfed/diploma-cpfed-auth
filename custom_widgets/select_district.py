from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.conf import settings

from locations.management.commands.create_regions import get_regions_json


class SelectDistrictWidget(Widget):
    template_name = None

    def render(self, name, value, attrs=None, renderer=None):
        context = super().get_context(name, value, attrs)
        context.update(regions=get_regions_json())
        return render_to_string("widgets/select_district.html", context=context)
