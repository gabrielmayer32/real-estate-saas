from django.core.management.base import BaseCommand
from properties.models import Property, PropertyPriceHistory

class Command(BaseCommand):
    help = 'Get property with id 9999 and its price history'

    def handle(self, *args, **kwargs):
        try:
            property = Property.objects.get(id=2066)
            price_history = PropertyPriceHistory.objects.filter(property=property).order_by('date')

            print(f"Property: {property.title}, Location: {property.location}, Current Price: {property.price} with ref : {property.ref}")
            print("Price History:")
            for history in price_history:
                print(f"Date: {history.date}, Price: {history.price}")

        except Property.DoesNotExist:
            print("Property with id 9999 does not exist.")
