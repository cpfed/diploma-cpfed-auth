import json

from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.conf import settings

with open(settings.BASE_DIR / 'locations' / 'regions.json', 'r', encoding='utf-8') as f:
    regions = json.dumps(json.load(f), ensure_ascii=False)

class SelectDistrictWidget(Widget):
    template_name = None
    def render(self, name, value, attrs=None, renderer=None):
        context = super().get_context(name, value, attrs)
        context.update(regions=regions)
        return render_to_string("widgets/select_district.html", context=context)
