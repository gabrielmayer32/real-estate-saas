import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns
# Load the JSON data into a DataFrame
with open('./scraping/', 'r') as file:
    data = json.load(file)

df = pd.DataFrame(data)

# Clean the price column
def clean_price(price):
    if isinstance(price, str):
        # Remove non-numeric characters
        clean_price = re.sub(r'[^\d.]', '', price)
        return float(clean_price) if clean_price else None
    return None

df['price'] = df['price'].apply(clean_price)

# Handle the description column: Convert lists to strings
df['description'] = df['description'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Handle missing values (if any)
df.fillna('', inplace=True)

# Extract number of bedrooms from the title
df['bedrooms'] = df['title'].str.extract(r'(\d+)\s*Bedrooms').astype(float)

# Extract size from the title
df['size'] = df['title'].str.extract(r'(\d+)\s*m²').astype(float)

# Display the DataFrame with new features
print(df[['title', 'bedrooms', 'size', 'price']].head())

# Use an interactive backend
plt.switch_backend('TkAgg')

# Price distribution
plt.figure(figsize=(10, 6))
sns.histplot(df['price'], bins=50, kde=True)
plt.title('Price Distribution')
plt.xlabel('Price (Rs)')
plt.ylabel('Frequency')
plt.savefig('price_distribution.png')
plt.show()

# Size vs. Price
plt.figure(figsize=(10, 6))
sns.scatterplot(x='size', y='price', data=df)
plt.title('Size vs. Price')
plt.xlabel('Size (m²)')
plt.ylabel('Price (Rs)')
plt.savefig('size_vs_price.png')
plt.show()

# Bedrooms vs. Price
plt.figure(figsize=(10, 6))
sns.boxplot(x='bedrooms', y='price', data=df)
plt.title('Bedrooms vs. Price')
plt.xlabel('Number of Bedrooms')
plt.ylabel('Price (Rs)')
plt.savefig('bedrooms_vs_price.png')
plt.show()