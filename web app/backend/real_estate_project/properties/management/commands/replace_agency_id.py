from django.core.management.base import BaseCommand
from properties.models import Property, Agency

class Command(BaseCommand):
    help = 'Populate agency_id field in Property model based on agency_name field'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        updated_count = 0
        missing_count = 0

        for property in properties:
            agency_name = property.agency_name
            if agency_name:
                try:
                    agency = Agency.objects.get(name=agency_name)
                    property.agency = agency
                    property.save()
                    updated_count += 1
                except Agency.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Agency '{agency_name}' does not exist for property ID {property.id}"))
                    missing_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} properties with agency_id'))
        if missing_count > 0:
            self.stdout.write(self.style.WARNING(f'{missing_count} properties have missing or non-existent agency names'))
