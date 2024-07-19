from django.core.management.base import BaseCommand
from properties.models import Property

class Command(BaseCommand):
    help = 'Clean interior_surface data and handle invalid inputs'

    def handle(self, *args, **kwargs):
        for property in Property.objects.all():
            try:
                if property.interior_surface and property.interior_surface.strip():
                    cleaned_surface = float(property.interior_surface.replace('m²', '').strip())
                    property.interior_surface = str(cleaned_surface)
                else:
                    property.interior_surface = None  # or set to 0.0 if you prefer
                property.save()
            except (ValueError, AttributeError):
                print(f"Skipping property ID {property.id} due to invalid data: {property.interior_surface}")
                continue

        self.stdout.write(self.style.SUCCESS('Successfully cleaned interior_surface data'))
