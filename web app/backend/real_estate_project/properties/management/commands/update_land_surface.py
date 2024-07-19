import csv
import re
from django.core.management.base import BaseCommand
from properties.models import Property

class Command(BaseCommand):
    help = 'Updates land_surface field in the Property model from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing the updates')

    def handle(self, *args, **options):
        path = options['csv_file']
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ref = row['ref']
                land_surface = row['land_surface']
                # Clean the land_surface to remove non-numeric characters and convert to float
                try:
                    # Remove non-numeric except decimal point
                    cleaned_surface = re.sub(r'[^\d.]+', '', land_surface)
                    # Convert to float
                    if cleaned_surface:  # Ensure it's not empty after cleaning
                        land_surface_value = float(cleaned_surface)
                        Property.objects.filter(ref=ref).update(land_surface=land_surface_value)
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated ref {ref} with land surface {land_surface_value}'))
                    else:
                        raise ValueError("Cleaned land surface is empty")
                except ValueError as e:
                    self.stdout.write(self.style.ERROR(f'Invalid land_surface for ref {ref}: {land_surface}. Error: {str(e)}'))
