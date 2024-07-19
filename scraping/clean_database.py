import json
import pandas as pd

# Load JSON data from a file
with open('./scraping/properties.json', 'r') as file:
    json_data = json.load(file)

# Function to clean individual fields
def clean_field(field):
    if isinstance(field, list):
        return ", ".join(field)
    if field is None:
        return ""
    return str(field).strip()

# Normalize the data
cleaned_data = []
for item in json_data:
    flattened_item = {
        "title": clean_field(item.get("title")),
        "location": clean_field(item.get("location")),
        "price": clean_field(item.get("price")),
        "details_link": clean_field(item.get("details_link")),
        "description": clean_field(item.get("description")),
        "agency": clean_field(item.get("agency")),
        "agency_logo": clean_field(item.get("agency_logo")),
        "contact_phone": clean_field(item.get("contact_phone")),
        "contact_email": clean_field(item.get("contact_email")),
        "contact_whatsapp": clean_field(item.get("contact_whatsapp")),
        "land_surface": clean_field(item.get("land_surface")),
        "interior_surface": clean_field(item.get("interior_surface")),
        "swimming_pool": clean_field(item.get("swimming_pool")),
        "construction_year": clean_field(item.get("construction_year")),
        "bedrooms": clean_field(item.get("bedrooms")),
        "accessible_to_foreigners": clean_field(item.get("accessible_to_foreigners")),
        "bathrooms": clean_field(item.get("bathrooms")),
        "toilets": clean_field(item.get("toilets")),
        "aircon": clean_field(item.get("aircon")),
        "general_features": clean_field(item.get("general_features")),
        "indoor_features": clean_field(item.get("indoor_features")),
        "outdoor_features": clean_field(item.get("outdoor_features")),
        "location_description": clean_field(item.get("location_description")),
    }
    cleaned_data.append(flattened_item)

# Convert to DataFrame
df = pd.DataFrame(cleaned_data)

# Save to CSV
df.to_csv("real_estate_listings.csv", index=False)

print("Data cleaned and saved to CSV successfully!")
