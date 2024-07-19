import csv
from django.core.management.base import BaseCommand
from properties.models import Property, PropertyPriceHistory, Agency
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import properties from a CSV file'

    def handle(self, *args, **kwargs):
        existing_refs = set(Property.objects.values_list('ref', flat=True))
        csv_refs = set()

        with open('../../../scraping/cleaned_properties_with_type.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not row['ref']:
                    continue

                ref = row['ref'].strip()

                csv_refs.add(ref)

                def convert_to_int(value):
                    if value:
                        try:
                            return int(float(value))
                        except (ValueError, TypeError):
                            return None
                    return None

                def convert_to_float(value):
                    if value:
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return None
                    return None

                bedrooms = convert_to_int(row['bedrooms'])
                bathrooms = convert_to_int(row['bathrooms'])
                toilets = convert_to_int(row['toilets'])
                price = convert_to_float(row['price'])
                land_surface = row['land_surface'].replace(' m²', '').replace(',', '') if row['land_surface'] else None
                interior_surface = row['interior_surface'].replace(' m²', '').replace(',', '') if row['interior_surface'] else None

                print(f"Processing row: {row}")

                def truncate(value, max_length):
                    if len(value) > max_length:
                        print(f"Truncating value: {value} to max length of {max_length}")
                        return value[:max_length]
                    return value

                # Find or create the Agency
                agency_name = truncate(row['agency'], 255)
                agency, created = Agency.objects.get_or_create(name=agency_name)
                if created:
                    print(f"Created new agency with name {agency_name}")

                try:
                    property = Property.objects.filter(ref=ref).first()
                    if property:
                        if property.price != price:
                            PropertyPriceHistory.objects.create(property=property, price=price)
                            property.price = price
                        property.last_updated = timezone.now()
                        property.sold = False  # Ensure it's marked as not sold
                        property.agency = agency  # Update the agency
                        property.save()
                        print(f"Updated property with ref {ref}.")
                    else:
                        Property.objects.create(
                            title=truncate(row['title'], 255),
                            location=truncate(row['location'], 255),
                            price=price,
                            details_link=row['details_link'],
                            description=row['description'],
                            agency=agency,  # Set the agency
                            agency_logo=row['agency_logo'],
                            contact_phone=truncate(row['contact_phone'], 50),
                            contact_email=truncate(row['contact_email'], 50),
                            contact_whatsapp=truncate(row['contact_whatsapp'], 50),
                            land_surface=convert_to_float(land_surface),
                            interior_surface=convert_to_float(interior_surface),
                            swimming_pool=truncate(row['swimming_pool'], 50),
                            construction_year=truncate(row['construction_year'], 4),
                            bedrooms=bedrooms,
                            accessible_to_foreigners=row['accessible_to_foreigners'] == 'Yes',
                            bathrooms=bathrooms,
                            toilets=toilets,
                            aircon=row['aircon'] == 'Yes',
                            general_features=row['general_features'],
                            indoor_features=row['indoor_features'],
                            outdoor_features=row['outdoor_features'],
                            location_description=row['location_description'],
                            type=truncate(row['type'], 50),
                            ref=truncate(ref, 50),
                            last_updated=timezone.now(),
                            sold=False  # New properties are not sold by default
                        )
                        print(f"Created new property with ref {ref}.")
                except Exception as e:
                    print(f"Error processing row: {row}")
                    print(f"Error: {e}")
                    continue

        # Step 3: Mark properties as sold if they haven't been updated in the last 6 months
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        properties_to_mark_sold = Property.objects.filter(last_updated__lt=six_months_ago, sold=False)
        for property in properties_to_mark_sold:
            property.sold = True
            property.save()
            print(f"Marked property with ref {property.ref} as sold.")



# import csv
# from django.core.management.base import BaseCommand
# from properties.models import Property

# class Command(BaseCommand):
#     help = 'Import properties from a CSV file'

#     def handle(self, *args, **kwargs):
#         with open('../../cleaned_properties.csv', newline='') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 # Skip rows where 'ref' is null
#                 if not row['ref']:
#                     continue

#                 # Skip if ref already exists
#                 if Property.objects.filter(ref=row['ref']).exists():
#                     print(f"Property with ref {row['ref']} already exists. Skipping.")
#                     continue

#                 # Convert float strings to integers for relevant fields if value is present
#                 def convert_to_int(value):
#                     if value:
#                         try:
#                             return int(float(value))
#                         except (ValueError, TypeError):
#                             return None
#                     return None

#                 # Convert to float for price and similar fields if value is present
#                 def convert_to_float(value):
#                     if value:
#                         try:
#                             return float(value)
#                         except (ValueError, TypeError):
#                             return None
#                     return None

#                 # Convert and assign the values
#                 bedrooms = convert_to_int(row['bedrooms'])
#                 bathrooms = convert_to_int(row['bathrooms'])
#                 toilets = convert_to_int(row['toilets'])
#                 price = convert_to_float(row['price'])
#                 land_surface = row['land_surface'].replace(' m²', '').replace(',', '') if row['land_surface'] else None
#                 interior_surface = row['interior_surface'].replace(' m²', '').replace(',', '') if row['interior_surface'] else None

#                 # Debug: Print the row to verify data
#                 print(f"Processing row: {row}")

#                 # Check length constraints and truncate if necessary
#                 def truncate(value, max_length):
#                     if len(value) > max_length:
#                         print(f"Truncating value: {value} to max length of {max_length}")
#                         return value[:max_length]
#                     return value

#                 try:
#                     Property.objects.create(
#                         title=truncate(row['title'], 255),
#                         location=truncate(row['location'], 255),
#                         price=price,
#                         details_link=row['details_link'],
#                         description=row['description'],
#                         agency=truncate(row['agency'], 255),
#                         agency_logo=row['agency_logo'],
#                         contact_phone=truncate(row['contact_phone'], 50),
#                         contact_email=truncate(row['contact_email'], 50),
#                         contact_whatsapp=truncate(row['contact_whatsapp'], 50),
#                         land_surface=convert_to_float(land_surface),
#                         interior_surface=convert_to_float(interior_surface),
#                         swimming_pool=truncate(row['swimming_pool'], 50),
#                         construction_year=truncate(row['construction_year'], 4),
#                         bedrooms=bedrooms,
#                         accessible_to_foreigners=row['accessible_to_foreigners'] == 'Yes',
#                         bathrooms=bathrooms,
#                         toilets=toilets,
#                         aircon=row['aircon'] == 'Yes',
#                         general_features=row['general_features'],
#                         indoor_features=row['indoor_features'],
#                         outdoor_features=row['outdoor_features'],
#                         location_description=row['location_description'],
#                         type=truncate(row['type'], 50),
#                         ref=truncate(row['ref'], 50),
#                     )
#                 except Exception as e:
#                     print(f"Error processing row: {row}")
#                     print(f"Error: {e}")
#                     continue
