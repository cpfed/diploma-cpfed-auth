import json

from django.core.management.base import BaseCommand
from django.conf import settings

from locations.models import Region

with open(settings.BASE_DIR/'locations'/'regions.json', 'r', encoding='utf-8') as f:
    regions = json.load(f)

class Command(BaseCommand):
    help = "Create regions"

    def handle(self, *args, **options):
        for region in regions:
            region_name = region.get("name")
            if not Region.objects.filter(name=region_name).exists():
                Region.objects.create(name=region_name)
                self.stdout.write(self.style.SUCCESS(f"Added {region.get('name')}"))
