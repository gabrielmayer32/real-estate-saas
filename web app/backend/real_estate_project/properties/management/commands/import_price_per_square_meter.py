from django.core.management.base import BaseCommand
from properties.models import Property, Region, PricePerSquareMeter

class Command(BaseCommand):
    help = 'Calculate and import price per square meter data from Property model'

    def handle(self, *args, **kwargs):
        # Step 1: Clear existing PricePerSquareMeter entries
        PricePerSquareMeter.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing PricePerSquareMeter data.'))

        # Step 2: Process each property in the database
        properties = Property.objects.all()
        for property in properties:
            if property.interior_surface and property.interior_surface > 0:  # Ensure there is a valid interior_surface
                try:
                    # Calculate price per square meter
                    price_per_square_meter = property.price / property.interior_surface

                    # Determine region from the property's region field or use the location field
                    if property.region:
                        region_name = property.region.name
                    else:
                        if ',' in property.location:
                            region_name = property.location.split(',')[1].strip()
                            self.stdout.write(self.style.WARNING(f'Property {property.id} has no region assigned. Extracted region from location: {region_name}'))
                        else:
                            region_name = 'Unknown'
                            self.stdout.write(self.style.WARNING(f'Property {property.id} has no region assigned and no comma in location.'))

                    region, created = Region.objects.get_or_create(name=region_name)

                    # Create or update the PricePerSquareMeter entry
                    PricePerSquareMeter.objects.update_or_create(
                        property_type=property.type,
                        region=region,
                        defaults={'price_per_square_meter': price_per_square_meter}
                    )

                    self.stdout.write(self.style.SUCCESS(f'Processed property {property.id} in region {region_name}.'))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing property {property.id}: {e}'))
            else:
                self.stdout.write(self.style.WARNING(f'Skipped property {property.id} due to invalid interior_surface.'))

        self.stdout.write(self.style.SUCCESS('Successfully recalculated and imported price per square meter data'))
