from django.core.management.base import BaseCommand
from locations.models import Region

regions = [
    {
        "name": "Астана"
    },
    {
        "name": "Алматы"
    },
    {
        "name": "Шымкент"
    },
    {
        "name": "Алматинская область"
    },
    {
        "name": "Акмолинская область"
    },
    {
        "name": "Атырауская область"
    },
    {
        "name": "Актюбинская область"
    },
    {
        "name": "Восточно-Казахстанская область"
    },
    {
        "name": "Жамбылская область"
    },
    {
        "name": "Западно-Казахстанская область"
    },
    {
        "name": "Карагандинская область"
    },
    {
        "name": "Костанайская область"
    },
    {
        "name": "Кызылординская область"
    },
    {
        "name": "Мангистауская область"
    },
    {
        "name": "Павлодарская область"
    },
    {
        "name": "Северо-Казахстанская область"
    },
    {
        "name": "Туркестанская область"
    },
    {
        "name": "Абайская область"
    },
    {
        "name": "Жетысуйская область"
    },
    {
        "name": "Улытауская область"
    },
]


class Command(BaseCommand):
    help = "Create regions"

    def handle(self, *args, **options):
        for region in regions:
            region_name = region.get("name")
            if not Region.objects.filter(name=region_name).exists():
                Region.objects.create(name=region_name)
                self.stdout.write(self.style.SUCCESS(f"Added {region.get('name')}"))
