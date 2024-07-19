from django.core.management.base import BaseCommand
from properties.models import Property, Agency

class Command(BaseCommand):
    help = 'Populates the Agency model with distinct agencies from Property model'

    def handle(self, *args, **options):
        # Fetch distinct agencies from the Property model
        agencies = Property.objects.values('agency', 'agency_logo', 'contact_phone', 'contact_email', 'contact_whatsapp').distinct()
        
        # Iterate through each unique agency and create an Agency model instance
        for agency_data in agencies:
            agency, created = Agency.objects.get_or_create(
                name=agency_data['agency'],
                defaults={

                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added agency: {agency.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Agency already exists: {agency.name}'))

        self.stdout.write(self.style.SUCCESS('Completed populating agencies.'))
