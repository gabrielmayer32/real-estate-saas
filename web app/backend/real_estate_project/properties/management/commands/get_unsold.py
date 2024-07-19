import requests
from django.core.management.base import BaseCommand
from properties.models import Property
import time

class Command(BaseCommand):
    help = 'Update sold properties based on their detail link'

    def handle(self, *args, **kwargs):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Load checked properties from a file
        checked_ids = set()
        try:
            with open('checked_properties.txt', 'r') as file:
                data = file.read().strip()
                if data:
                    checked_ids = set(map(int, data.split()))
                else:
                    self.stdout.write(self.style.NOTICE('checked_properties.txt is empty, checking all properties.'))
        except FileNotFoundError:
            self.stdout.write(self.style.NOTICE('checked_properties.txt not found, checking all properties.'))

        # Debug: Print total properties in the database
        total_properties_in_db = Property.objects.count()
        self.stdout.write(self.style.NOTICE(f'Total properties in the database: {total_properties_in_db}'))

        # Fetch all properties, excluding the ones already checked
        if checked_ids:
            properties_to_check = Property.objects.exclude(id__in=checked_ids)
        else:
            properties_to_check = Property.objects.all()

        total_properties = properties_to_check.count()
        updated_properties = 0

        self.stdout.write(self.style.NOTICE(f'Total properties to check: {total_properties}'))

        if total_properties == 0:
            self.stdout.write(self.style.NOTICE('No properties to check.'))
            return

        for property in properties_to_check:
            try:
                response = requests.get(property.details_link, headers=headers)
                if response.status_code == 200:
                    print(f'Checking property {property.id} {property.details_link}')
                    if 'en/buy-mauritius/' in response.url:
                        if response.url != property.details_link:
                            property.sold = True
                            property.save()
                            updated_properties += 1
                            self.stdout.write(self.style.SUCCESS(f'Updated property {property.id} as sold.'))
                    else:
                        self.stdout.write(self.style.NOTICE(f'Property {property.id} remains unsold.'))
                        
                else:
                    self.stdout.write(self.style.WARNING(f'Failed to fetch URL for property {property.id}: Status Code {response.status_code}'))

                # Add the checked property ID to the set
                checked_ids.add(property.id)
                time.sleep(2)

            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Error fetching URL for property {property.id}: {e}'))

            # Save the updated set of checked property IDs to a file after each iteration
            with open('checked_properties.txt', 'w') as file:
                file.write(' '.join(map(str, checked_ids)))

        self.stdout.write(self.style.SUCCESS(f'Processed {total_properties} properties. Updated {updated_properties} properties as sold.'))
