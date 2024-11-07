from django.core.management.base import BaseCommand
from django.core import serializers
from core.models import Stock


# "export_product_residue" command
class Command(BaseCommand):
    help = "Export product residue to a JSON file"

    def handle(self, *args, **kwargs):
        data = serializers.serialize("json", Stock.objects.all())
        with open("src/core/management/commands/stock_data.json", "w") as file:
            file.write(data)
        self.stdout.write(self.style.SUCCESS("Successfully exported product residue"))
