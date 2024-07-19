import csv
from django.core.management.base import BaseCommand
from properties.models import Property

class Command(BaseCommand):
    help = 'Mark properties as sold if their ref is not present in the given CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing current properties')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        current_refs = set()
        
        # Read the CSV file and collect all refs
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                current_refs.add(row['ref'])
        
        # Find and mark properties as sold if their ref is not in the current_refs
        properties_to_update = Property.objects.exclude(ref__in=current_refs)
        updated_count = properties_to_update.update(sold=True)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully marked {updated_count} properties as sold.'))
