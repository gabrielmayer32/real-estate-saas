import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV into a DataFrame
df = pd.read_csv('Land undervalued by region - real_estate_listings_modified.csv')

# Clean and convert 'price' column to numeric, handling 'Price N/D'
df['price_cleaned'] = pd.to_numeric(df['price'].str.replace('Rs ', '').str.replace(',', ''), errors='coerce')

# Function to retrieve property details by ID
def get_property_details(property_id):
    return df[df['ID'] == property_id]

# Example property ID to compare
property_id = 10701
property_details = get_property_details(property_id)

# Criteria for filtering similar properties
region = property_details['location'].iloc[0]  # Assuming 'location' is the region
num_bedrooms = property_details['bedrooms'].iloc[0]
construction_year = property_details['construction_year'].iloc[0]

# Convert land_surface and interior_surface columns to numeric, handling errors
df['land_surface'] = pd.to_numeric(df['land_surface'].str.replace(' m²', ''), errors='coerce')
df['interior_surface'] = pd.to_numeric(df['interior_surface'].str.replace(' m²', ''), errors='coerce')

# Calculate thresholds for land and interior surface
property_land_surface = pd.to_numeric(property_details['land_surface'].str.replace(' m²', ''), errors='coerce').iloc[0]
property_interior_surface = pd.to_numeric(property_details['interior_surface'].str.replace(' m²', ''), errors='coerce').iloc[0]

land_surface_threshold = property_land_surface * 0.2
interior_surface_threshold = property_interior_surface * 0.2

# Filter properties only of type 'House' or 'Apartment' within the similarity threshold
filtered_properties = df[
    df['type'].isin(['House', 'Apartment']) &
    (df['ID'] != property_id) &  # Exclude the property itself
    (df['location'] == region) &
    (df['bedrooms'] == num_bedrooms) &
    (df['construction_year'] == construction_year) &
    (
        ((df['swimming_pool'] == 'Private pool') | 
         (df['swimming_pool'] == 'Common pool') | 
         (df['swimming_pool'].isna()))  # Include properties with no swimming pool information ('Else')
    ) &
    ((df['land_surface'] >= property_land_surface - land_surface_threshold) &
     (df['land_surface'] <= property_land_surface + land_surface_threshold)) &
    ((df['interior_surface'] >= property_interior_surface - interior_surface_threshold) &
     (df['interior_surface'] <= property_interior_surface + interior_surface_threshold))
]

# Data Visualization
plt.figure(figsize=(12, 8))

# Plotting the original property
plt.scatter(property_land_surface, property_interior_surface, color='blue', label=f'Property {property_id}', s=100)

# Plotting similar properties
plt.scatter(filtered_properties['land_surface'], filtered_properties['interior_surface'], color='red', label='Similar Properties', alpha=0.5)

# Adding labels and titles
plt.title(f'Comparison of Property {property_id} with Similar Properties (House/Apartment)')
plt.xlabel('Land Surface (m²)')
plt.ylabel('Interior Surface (m²)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()