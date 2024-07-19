import csv
from django.core.management.base import BaseCommand
from properties.models import Location

class Command(BaseCommand):
    help = 'Import locations from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    name, region = row['location'].split(', ')
                    latitude = float(row['latitude']) if row['latitude'] else None
                    longitude = float(row['longitude']) if row['longitude'] else None
                    location, created = Location.objects.update_or_create(
                        name=name,
                        region=region,
                        defaults={'latitude': latitude, 'longitude': longitude}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created location {name}, {region}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Updated location {name}, {region}"))
                except ValueError as e:
                    self.stderr.write(self.style.ERROR(f"Skipping row {row} due to error: {e}"))

