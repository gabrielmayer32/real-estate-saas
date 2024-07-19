#!/bin/bash

# Activate the virtual environment
source ../../myenv/bin/activate

cd "/Users/gabrielmayer/Desktop/real estate micro Saas/scraping"
python combined-spiders.py

# Remove duplicates
python remove_duplicates.py
python extract_type_csv.py

# Import data to the database
cd "/Users/gabrielmayer/Desktop/real estate micro Saas/web app/backend/real_estate_project"
python manage.py import_properties
python manage.py clean_interior
python manage.py clean_land_surface
python manage.py import_price_per_square_meter
python manage.py mark_as_sold
python manage.py fetch_exchange_rate
# get_unsold

# Step 4: Remove the old CSV file
rm "/Users/gabrielmayer/Desktop/real estate micro Saas/scraping/test_new_db.csv"
rm "/Users/gabrielmayer/Desktop/real estate micro Saas/scraping/cleaned_properties_with_type.csv"
rm "/Users/gabrielmayer/Desktop/real estate micro Saas/scraping/cleaned_properties.csv"


# Deactivate the virtual environment
deactivate


# import_locations.py
# extract_type_csv
# clean_interior
# clean_land_surface
# remove_duplicates
# mark_as_sold
# import_price_per_square_meter.py
# fetch_exchange_rate.py