import json
from django.core.management.base import BaseCommand
from core.models import Product, Stock


# "load_goods" command
class Command(BaseCommand):
    help = 'Load goods from a JSON file'

    def handle(self, *args, **kwargs):
        with open('src/core/management/commands/example_goods.json') as file:
            data = json.load(file)
            for item in data:
                product, created = Product.objects.get_or_create(
                    name=item['name'],
                    defaults={
                        'description': item['description'],
                        'price': item['price']
                    }
                )
                Stock.objects.get_or_create(
                    product=product,
                    defaults={'quantity': item['quantity']}
                )
        self.stdout.write(self.style.SUCCESS('Successfully loaded goods'))
