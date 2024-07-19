import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from matplotlib.ticker import FuncFormatter, ScalarFormatter
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
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

# Convert swimming_pool column to dummy variables
df = pd.get_dummies(df, columns=['swimming_pool'], prefix='pool')

# Convert accessible_to_foreigners column to binary
df['accessible_to_foreigners'] = df['accessible_to_foreigners'].apply(lambda x: 1 if x == 'Yes' else 0)

# Formatter functions
def currency_formatter(x, pos):
    return f'Rs {x:,.0f}'

def size_formatter(x, pos):
    return f'{x:,.0f} m²'

# Function to create safe filenames
def safe_filename(filename):
    return re.sub(r'\W+', '_', filename)

# Get user input for property type and run the process_data function
property_type = input("Enter the property type to filter (e.g., 'House / Villa', 'Apartment', etc.): ")

# Define feature sets for different property types
feature_sets = {
    'House / Villa': ['land_surface', 'interior_surface', 'bedrooms', 'aircon', 
                      'pool_Common pool', 'pool_Private pool', 'accessible_to_foreigners'],
    'Apartment': ['interior_surface', 'bedrooms', 'aircon', 
                  'pool_Common pool', 'pool_Private pool', 'accessible_to_foreigners'],
    # Add other property types and their respective features as needed
}

# Select the appropriate feature set based on the property type
features = feature_sets.get(property_type, [])

if not features:
    print(f"No features defined for property type: {property_type}")
else:
    # Filter data for the selected property type
    subset = df[df['type'] == property_type]

    if subset.empty:
        print(f"No data available for property type: {property_type}")
    else:
        # Filter out rows with missing values in the selected features
        subset = subset.dropna(subset=features + ['price'])

        if subset.empty:
            print(f"Not enough data available for property type: {property_type} after filtering.")
        else:
            # Prepare data for regression
            X = subset[features]
            y = subset['price']

            # Standardize the features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Linear Regression
            lin_reg_model = LinearRegression()
            lin_reg_model.fit(X_scaled, y)
            lin_reg_importance = lin_reg_model.coef_

            # Random Forest Regression
            rf_model = RandomForestRegressor()
            rf_model.fit(X, y)
            rf_importance = rf_model.feature_importances_

            # Create DataFrames for feature importance
            lin_reg_feature_importance = pd.DataFrame({
                'Feature': features,
                'Importance': lin_reg_importance
            }).sort_values(by='Importance', ascending=False)

            rf_feature_importance = pd.DataFrame({
                'Feature': features,
                'Importance': rf_importance
            }).sort_values(by='Importance', ascending=False)

            # Display the feature importance
            print("Linear Regression Feature Importance:")
            print(lin_reg_feature_importance.to_string(index=False, formatters={'Importance': '{:,.6f}'.format}))
            print("\nRandom Forest Feature Importance:")
            print(rf_feature_importance.to_string(index=False, formatters={'Importance': '{:,.6f}'.format}))

            # Plot feature importance
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1)
            sns.barplot(x='Importance', y='Feature', data=lin_reg_feature_importance, palette='viridis')
            plt.title(f'Linear Regression Feature Importance for {property_type}')
            plt.xlabel('Importance')
            plt.ylabel('Feature')
            plt.grid(True)
            plt.gca().xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
            plt.xticks(rotation=45, ha='right')

            plt.subplot(1, 2, 2)
            sns.barplot(x='Importance', y='Feature', data=rf_feature_importance, palette='viridis')
            plt.title(f'Random Forest Feature Importance for {property_type}')
            plt.xlabel('Importance')
            plt.ylabel('Feature')
            plt.grid(True)
            plt.gca().xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
            plt.xticks(rotation=45, ha='right')

            plt.tight_layout()
            plt.show()
