import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from matplotlib.ticker import ScalarFormatter
from sklearn.linear_model import LinearRegression
import numpy as np

# Load the CSV data
df = pd.read_csv("real_estate_listings_modified.csv")

# Function to extract type from title
def extract_type(title):
    if isinstance(title, str):
        return title.split(' - ')[0]
    return "Unknown"

# Apply the function to create the 'type' column
df['type'] = df['title'].apply(extract_type)

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

# Function to create safe filenames
def safe_filename(filename):
    return re.sub(r'\W+', '_', filename)

# Get user input for property type
property_type = input("Enter the property type to filter (e.g., 'House / Villa', 'Apartment', etc.): ")

# Filter data for the selected property type
subset = df[df['type'] == property_type]

if subset.empty:
    print(f"No data available for property type: {property_type}")
else:
    # Filter out rows with missing values in the selected features
    subset = subset.dropna(subset=['interior_surface', 'price'])

    if subset.empty:
        print(f"Not enough data available for property type: {property_type} after filtering.")
    else:
        # Prepare data for regression
        X = subset[['interior_surface']]
        y = subset['price']

        # Fit a linear regression model
        lin_reg_model = LinearRegression()
        lin_reg_model.fit(X, y)
        y_pred = lin_reg_model.predict(X)

        # Plot the relationship between interior_surface and price
        plt.figure(figsize=(10, 6))
        plt.scatter(subset['interior_surface'], subset['price'], alpha=0.6, edgecolors='w', linewidth=0.5, label='Data Points')

        # Annotate IDs near the dots
        for i, row in subset.iterrows():
            plt.annotate(row['ID'], (row['interior_surface'], row['price']), textcoords="offset points", xytext=(5,5), ha='center', fontsize=8)

        plt.plot(subset['interior_surface'], y_pred, color='red', linewidth=2, label='Linear Regression Line')
        plt.title(f'Interior Surface vs. Price for {property_type}')
        plt.xlabel('Interior Surface Area (m²)')
        plt.ylabel('Price (Rs)')
        plt.legend()
        plt.grid(True)
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False, useMathText=False))
        plt.gca().ticklabel_format(style='plain', axis='y')
        plt.show()

        # Display the linear regression coefficients
        print(f"Linear Regression Coefficients for {property_type}:")
        print(f"Intercept: {lin_reg_model.intercept_}")
        print(f"Coefficient: {lin_reg_model.coef_[0]}")
