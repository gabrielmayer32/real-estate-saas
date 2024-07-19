import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV into a DataFrame
df = pd.read_csv('Land undervalued by region - real_estate_listings_modified.csv')

# Clean and convert 'price' column to numeric, handling 'Price N/D'
df['price_cleaned'] = pd.to_numeric(df['price'].str.replace('Rs ', '').str.replace(',', ''), errors='coerce')

# Filter out rows where price could not be converted
df_valid_prices = df.dropna(subset=['price_cleaned'])

# Calculate average prices by agency
average_prices = df_valid_prices.groupby('agency')['price_cleaned'].mean()

# Calculate differences between actual prices and average prices by agency
df_valid_prices['average_price'] = df_valid_prices['agency'].map(average_prices)
df_valid_prices['price_difference'] = df_valid_prices['price_cleaned'] - df_valid_prices['average_price']

# Calculate percentage difference
df_valid_prices['percent_difference'] = (df_valid_prices['price_difference'] / df_valid_prices['average_price']) * 100

# Summary statistics
agency_stats = df_valid_prices.groupby('agency')['percent_difference'].agg(['mean', 'count'])

# Data Visualization - Dot Plot with Agency Names on Dots
plt.figure(figsize=(12, 8))

# Plotting the dots with agency names
sns.scatterplot(x='mean', y='agency', size='count', sizes=(50, 500),
                data=agency_stats, legend=False, hue='mean', palette='coolwarm')

# Annotate each point with agency name
for index, row in agency_stats.iterrows():
    plt.text(row['mean'] + 0.3, index, index, va='center', ha='left', fontsize=9, color='black', weight='bold')

# Adding labels and titles
plt.title('Mean Percentage Difference of Property Prices by Agency')
plt.xlabel('Mean Percentage Difference (%)')
plt.ylabel('Agency')
plt.grid(True)
plt.tight_layout()
plt.show()

# Save the results to a new file
df_valid_prices.to_csv('property_valuation_analysis.csv', index=False)