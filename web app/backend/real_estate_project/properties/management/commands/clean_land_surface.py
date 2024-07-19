from django.core.management.base import BaseCommand
from properties.models import Property

class Command(BaseCommand):
    help = 'Clean land_surface data and handle invalid inputs'

    def handle(self, *args, **kwargs):
        for property in Property.objects.all():
            try:
                if property.land_surface and property.land_surface.strip() and property.land_surface != "N.S":
                    cleaned_surface = float(property.land_surface.replace('m²', '').strip())
                    property.land_surface = str(cleaned_surface)
                else:
                    property.land_surface = None  # or set to 0.0 if you prefer
                property.save()
            except (ValueError, AttributeError):
                print(f"Skipping property ID {property.id} due to invalid data: {property.land_surface}")
                continue

        self.stdout.write(self.style.SUCCESS('Successfully cleaned land_surface data'))
