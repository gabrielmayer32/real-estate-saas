from django.core.management.base import BaseCommand
from django.db import models
from properties.models import Property

class Command(BaseCommand):
    help = 'Remove duplicate properties based on ref field'

    def handle(self, *args, **kwargs):
        # Find all properties with duplicate refs
        duplicates = Property.objects.values('ref').annotate(count_ref=models.Count('ref')).filter(count_ref__gt=1)

        for duplicate in duplicates:
            ref_value = duplicate['ref']
            # Find all properties with the same ref
            properties_with_same_ref = Property.objects.filter(ref=ref_value)
            # Keep only one property (the first one) and delete the rest
            properties_to_delete = properties_with_same_ref[1:]  # Exclude the first property
            for property_to_delete in properties_to_delete:
                property_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted duplicate property with ref {ref_value} and id {property_to_delete.id}'))

        self.stdout.write(self.style.SUCCESS('Successfully removed all duplicate properties'))
