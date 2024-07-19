from django.db import transaction
from decimal import Decimal, InvalidOperation
from properties.models import Property

def convert_land_surface():
    with transaction.atomic():  # Use atomic to ensure data integrity
        for property in Property.objects.all():
            try:
                # Attempt to convert and save the decimal value
                property.land_surface_decimal = Decimal(property.land_surface.replace(',', '.'))
                property.save()
            except InvalidOperation:
                # Handle conversion failure
                print(f"Failed conversion for property ID {property.id} with land_surface '{property.land_surface}'")
                # Set to default or leave as is for manual intervention
                property.land_surface_decimal = Decimal(0.0)
                property.save()

# Note: Add error handling or logging as needed
