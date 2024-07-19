from django.core.management.base import BaseCommand
from properties.models import Property

class Command(BaseCommand):
    help = 'Remove .0 suffix from ref in Property model'

    def handle(self, *args, **kwargs):
        properties = Property.objects.all()
        updated_count = 0

        for property in properties:
            if property.ref.endswith('.0'):
                property.ref = property.ref[:-2]
                property.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Removed .0 from ref {property.ref}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} properties'))
