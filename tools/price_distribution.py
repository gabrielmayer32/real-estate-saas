import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from matplotlib.ticker import FuncFormatter

# Load the CSV data
df = pd.read_csv("real_estate_listings_modified.csv")

# Add an ID column
# df.insert(0, 'ID', range(1, 1 + len(df)))

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

# Formatter functions
def currency_formatter(x, pos):
    return f'Rs {x:,.0f}'

def size_formatter(x, pos):
    return f'{x:,.0f} m²'

# Function to create safe filenames
def safe_filename(filename):
    return re.sub(r'\W+', '_', filename)

# Function to process data and generate plots
def process_data(property_type):
    safe_property_type = safe_filename(property_type)
    subset = df[df['type'] == property_type]
    
    if not subset.empty:
        plt.figure(figsize=(10, 6))
        sns.histplot(subset['price'].dropna(), bins=50, kde=True)
        plt.title(f'Price Distribution for {property_type}')
        plt.xlabel('Price (Rs)')
        plt.ylabel('Frequency')
        plt.gca().xaxis.set_major_formatter(FuncFormatter(currency_formatter))
        plt.savefig(f'price_distribution_{safe_property_type}.png')
        plt.show()
    else:
        print(f"No data available for property type: {property_type}")


# 2. Properties by Location (Top 30 Locations)
plt.figure(figsize=(12, 8))
location_counts = df['location'].value_counts().nlargest(30)
location_counts.plot(kind='bar', color='skyblue')
plt.title('Top 30 Locations by Number of Properties')
plt.xlabel('Location')
plt.ylabel('Number of Properties')
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.show()

# 3. Surface Area vs. Price
plt.figure(figsize=(10, 6))
plt.scatter(df['interior_surface'], df['price'], alpha=0.6, edgecolors='w', linewidth=0.5)
plt.title('Surface Area vs. Price')
plt.xlabel('Interior Surface Area (m²)')
plt.ylabel('Price (Rs)')
plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))
plt.grid(True)
plt.show()

# Get user input for property type and run the process_data function
property_type = input("Enter the property type to filter (e.g., 'House / Villa', 'Apartment', etc.): ")

# Run the process_data function with the chosen property type
process_data(property_type)
