import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from matplotlib.ticker import ScalarFormatter
from sklearn.linear_model import LinearRegression
import numpy as np
import os

# Load the CSV data
df = pd.read_csv("real_estate_listings_modified.csv")

# Function to extract type from title
def extract_type(title):
    if isinstance(title, str):
        return title.split(' - ')[0]
    return "Unknown"

# Apply the function to create the 'type' column
df['type'] = df['title'].apply(extract_type)

# Function to extract region from location
def extract_region(location):
    if isinstance(location, str):
        return location.split(',')[-1].strip()
    return "Unknown"

# Apply the function to create the 'region' column
df['region'] = df['location'].apply(extract_region)

# Function to clean and convert price to numeric
def clean_price(price):
    try:
        return float(price.replace('Rs', '').replace(',', '').strip())
    except:
        return None

# Apply the cleaning function to the price column
df['price'] = df['price'].apply(clean_price)

# Extract numerical values for land and interior surfaces, handling errors
df['land_surface'] = pd.to_numeric(df['land_surface'].str.extract('(\d+.\d+)')[0], errors='coerce')
df['interior_surface'] = pd.to_numeric(df['interior_surface'].str.extract('(\d+.\d+)')[0], errors='coerce')
df['construction_year'] = pd.to_numeric(df['construction_year'], errors='coerce')

# Function to create safe filenames
def safe_filename(filename):
    return re.sub(r'\W+', '_', filename)

# Get user input for property type and region
property_type = input("Enter the property type to filter (e.g., 'House / Villa', 'Apartment', etc.): ")
region = input("Enter the region to filter (e.g., 'North', 'West', etc.): ")

if region == "West":
    valid_locations = ["Black River, West", "Tamarin, West", "Chamarel, West"]
    # subset = df[(df['type'] == property_type) & (df['region'] == region) & 
    #             (df['location'].isin(valid_locations)) & (df['construction_year'] > 2012)]
    subset = df[(df['type'] == property_type) & (df['region'] == region) & 
                (df['location'].isin(valid_locations)) ]
else:
    # subset = df[(df['type'] == property_type) & (df['region'] == region) & (df['construction_year'] > 2012)]

    subset = df[(df['type'] == property_type) & (df['region'] == region)]

if subset.empty:
    print(f"No data available for property type: {property_type} in region: {region} with construction year > 2012")
else:
    # Filter out rows with missing values in the selected features
    subset = subset.dropna(subset=['land_surface', 'price'])

    if subset.empty:
        print(f"Not enough data available for property type: {property_type} in region: {region} with construction year > 2012 after filtering.")
    else:
        # Prepare data for regression
        X = subset[['land_surface']]
        y = subset['price']

        # Fit a linear regression model
        lin_reg_model = LinearRegression()
        lin_reg_model.fit(X, y)
        y_pred = lin_reg_model.predict(X)

        # Calculate residuals (actual price - predicted price)
        subset['residual'] = subset['price'] - y_pred

        # Define a threshold to identify undervalued properties (e.g., residual < -20% of predicted price)
        threshold = -0.2 * y_pred
        subset['undervalued'] = subset['residual'] < threshold

        # Plot the relationship between land_surface and price
        plt.figure(figsize=(12, 6))
        plt.scatter(subset['land_surface'], subset['price'], alpha=0.6, edgecolors='w', linewidth=0.5, label='Data Points')

        # Highlight undervalued properties
        undervalued = subset[subset['undervalued']]
        plt.scatter(undervalued['land_surface'], undervalued['price'], color='red', edgecolors='w', linewidth=0.5, label='Undervalued Properties')

        # Annotate IDs for all properties
        for i, row in subset.iterrows():
            plt.annotate(row['ID'], (row['land_surface'], row['price']), textcoords="offset points", xytext=(5,5), ha='center', fontsize=8, color='black')

        plt.plot(subset['land_surface'], y_pred, color='blue', linewidth=2, label='Linear Regression Line')
        plt.title(f'Land Surface vs. Price for {property_type} in {region} (Construction Year > 2012)')
        plt.xlabel('Land Surface Area (m²)')
        plt.ylabel('Price (Rs)')
        plt.legend()
        plt.grid(True)
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
        plt.gca().ticklabel_format(style='plain', axis='y')

        # Save the figure
        plot_filename = safe_filename(f"{region} - {property_type} - undervalued_property.png")
        plt.savefig(plot_filename)
        print(f"Plot saved as {plot_filename}")

        plt.show()
        plt.show()

        # Display the linear regression coefficients
        print(f"Linear Regression Coefficients for {property_type} in {region} (Construction Year > 2012):")
        print(f"Intercept: {lin_reg_model.intercept_}")
        print(f"Coefficient: {lin_reg_model.coef_[0]}")

        # Display undervalued properties
        if not undervalued.empty:
            print("\nUndervalued Properties:")
            print(undervalued[['ID', 'title', 'location', 'price', 'land_surface', 'residual', 'construction_year']])

            # Save undervalued properties to a new CSV file
            file_path = "undervalued_properties.csv"
            try:
                undervalued.to_csv(file_path, index=False)
                if os.path.exists(file_path):
                    print(f"Undervalued properties have been successfully saved to {file_path}.")
                else:
                    print("Failed to save the CSV file.")
            except Exception as e:
                print(f"An error occurred while saving the CSV file: {e}")
        else:
            print("No undervalued properties found.")
