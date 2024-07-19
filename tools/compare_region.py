import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

# Load the CSV data into a DataFrame
df = pd.read_csv('properties.csv')

# Display the first few rows of the DataFrame
print("Original DataFrame:")
print(df.head())

# Clean the price column
def clean_price(price):
    if isinstance(price, str):
        # Remove non-numeric characters
        clean_price = re.sub(r'[^\d.]', '', price)
        return float(clean_price) if clean_price else None
    return price

df['price'] = df['price'].apply(clean_price)

# Convert 'no room' and 'size (m²)' columns to numeric
df['no room'] = pd.to_numeric(df['no room'], errors='coerce')
df['size (m²)'] = pd.to_numeric(df['size (m²)'], errors='coerce')

# Fill NaN values in numeric columns with 0
df['price'] = df['price'].fillna(0)
df['no room'] = df['no room'].fillna(0)
df['size (m²)'] = df['size (m²)'].fillna(0)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Remove outliers - you may adjust the thresholds based on your dataset
df = df[(df['price'] < 1e8) & (df['size (m²)'] < 10000)]

# Ensure no NaN values in the 'location' column for filtering
df['location'] = df['location'].fillna('')
df['type'] = df['type'].fillna('')

# Get user input for the type of property to filter
property_type = input("Enter the property type to filter (e.g., 'House / Villa', 'Apartment', etc.): ")

# Filter data based on type
df = df[df['type'].str.contains(property_type, case=False, na=False)]

# Filter data for North and West regions
North_df = df[df['location'].str.contains('North', case=False)]
west_df = df[df['location'].str.contains('West', case=False)]

# Define a custom formatter to avoid scientific notation
def currency_formatter(x, pos):
    return f'Rs {x:,.0f}'

def size_formatter(x, pos):
    return f'{x:,.0f} m²'

# Use an interactive backend for plotting
plt.switch_backend('TkAgg')

# Function to create safe filenames
def safe_filename(filename):
    return re.sub(r'\W+', '_', filename)

# Generate safe filenames
safe_property_type = safe_filename(property_type)

# Price distribution comparison
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
sns.histplot(North_df['price'], bins=50, kde=True, color='blue', label='North')
plt.title('Price Distribution (North)')
plt.xlabel('Price (Rs)')
plt.ylabel('Frequency')
plt.gca().xaxis.set_major_formatter(FuncFormatter(currency_formatter))
plt.legend()

plt.subplot(1, 2, 2)
sns.histplot(west_df['price'], bins=50, kde=True, color='green', label='West')
plt.title('Price Distribution (West)')
plt.xlabel('Price (Rs)')
plt.ylabel('Frequency')
plt.gca().xaxis.set_major_formatter(FuncFormatter(currency_formatter))
plt.legend()

plt.tight_layout()
plt.savefig(f'price_distribution_comparison_{safe_property_type}.png')
plt.show()

# Size vs. Price comparison
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
sns.scatterplot(x='size (m²)', y='price', data=North_df, color='blue', label='North')
plt.title('Size vs. Price (North)')
plt.xlabel('Size (m²)')
plt.ylabel('Price (Rs)')
plt.gca().xaxis.set_major_formatter(FuncFormatter(size_formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))

plt.subplot(1, 2, 2)
sns.scatterplot(x='size (m²)', y='price', data=west_df, color='green', label='West')
plt.title('Size vs. Price (West)')
plt.xlabel('Size (m²)')
plt.ylabel('Price (Rs)')
plt.gca().xaxis.set_major_formatter(FuncFormatter(size_formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))

plt.tight_layout()
plt.savefig(f'size_vs_price_comparison_{safe_property_type}.png')
plt.show()

# Bedrooms vs. Price comparison
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
sns.boxplot(x='no room', y='price', data=North_df, color='blue')
plt.title('Bedrooms vs. Price (North)')
plt.xlabel('Number of Bedrooms')
plt.ylabel('Price (Rs)')
plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))

plt.subplot(1, 2, 2)
sns.boxplot(x='no room', y='price', data=west_df, color='green')
plt.title('Bedrooms vs. Price (West)')
plt.xlabel('Number of Bedrooms')
plt.ylabel('Price (Rs)')
plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))

plt.tight_layout()
plt.savefig(f'bedrooms_vs_price_comparison_{safe_property_type}.png')
plt.show()
