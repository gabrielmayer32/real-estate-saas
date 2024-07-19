import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import re
import numpy as np

# Load the CSV data
df = pd.read_csv("Land undervalued by region - real_estate_listings_modified.csv")

# Clean and process data
def extract_type(title):
    if isinstance(title, str):
        return title.split(' - ')[0]
    return "Unknown"

def extract_region(location):
    if isinstance(location, str):
        return location.split(',')[-1].strip()
    return "Unknown"

def clean_price(price):
    try:
        return float(price.replace('Rs', '').replace(',', '').strip())
    except:
        return None

df['type'] = df['title'].apply(extract_type)
df['region'] = df['location'].apply(extract_region)
df['price'] = df['price'].apply(clean_price)
df['land_surface'] = pd.to_numeric(df['land_surface'].str.extract('(\d+.\d+)')[0], errors='coerce')
df['construction_year'] = pd.to_numeric(df['construction_year'], errors='coerce')

# Filter data
df = df[df['construction_year'] <= 2023]

# Drop rows with NaN values in required columns
df = df.dropna(subset=['land_surface', 'price'])

# 1. Location Analysis
location_avg_price = df.groupby('location')['price'].mean().sort_values(ascending=False)
print("Average Price by Location:\n", location_avg_price)

# 2. Impact of Features on Price
features = ['land_surface', 'bedrooms', 'bathrooms', 'toilets', 'aircon']
for feature in features:
    plt.figure(figsize=(10, 6))
    sns.boxplot(x=feature, y='price', data=df)
    plt.title(f'Impact of {feature} on Price')
    plt.xlabel(feature)
    plt.ylabel('Price (Rs)')
    plt.show()

# 3. Property Type Segmentation
type_avg_price = df.groupby('type')['price'].mean().sort_values(ascending=False)
print("Average Price by Property Type:\n", type_avg_price)

# 4. Year of Construction Impact
plt.figure(figsize=(10, 6))
sns.lineplot(x='construction_year', y='price', data=df)
plt.title('Impact of Year of Construction on Price')
plt.xlabel('Year of Construction')
plt.ylabel('Price (Rs)')
plt.show()

# 5. Identifying Undervalued Properties
def find_undervalued_properties(df, feature):
    subset = df.dropna(subset=[feature, 'price'])
    X = subset[[feature]]
    y = subset['price']
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    subset['residual'] = subset['price'] - y_pred
    threshold = -0.2 * y_pred
    subset['undervalued'] = subset['residual'] < threshold
    undervalued_properties = subset[subset['undervalued']]
    return undervalued_properties, model

undervalued_by_land_surface, lin_reg_model = find_undervalued_properties(df, 'land_surface')
print("Undervalued Properties by Land Surface:\n", undervalued_by_land_surface[['ID', 'title', 'location', 'price', 'land_surface', 'residual']])

# Save undervalued properties to CSV
undervalued_by_land_surface.to_csv('undervalued_properties_by_land_surface.csv', index=False)

# Plot undervalued properties
plt.figure(figsize=(12, 6))
plt.scatter(df['land_surface'], df['price'], alpha=0.6, edgecolors='w', linewidth=0.5, label='Data Points')
plt.scatter(undervalued_by_land_surface['land_surface'], undervalued_by_land_surface['price'], color='red', edgecolors='w', linewidth=0.5, label='Undervalued Properties')
plt.plot(df['land_surface'], lin_reg_model.predict(df[['land_surface']]), color='green', linewidth=2, label='Linear Regression Line')
plt.title(f'Land Surface vs. Price (Undervalued Properties Highlighted)')
plt.xlabel('Land Surface Area (m²)')
plt.ylabel('Price (Rs)')
plt.legend()
plt.grid(True)
plt.show()
