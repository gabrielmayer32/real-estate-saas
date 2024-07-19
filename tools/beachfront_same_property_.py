import pandas as pd
import matplotlib.pyplot as plt

# Load the data from CSV (replace with your actual data source)
file_path = 'Land undervalued by region - real_estate_listings_modified.csv'
df = pd.read_csv(file_path)

# Example data loading check:
print("Initial DataFrame:")
print(df.head())

# Clean and convert columns to numeric values, handling errors
# Clean and convert price column
df['price'] = df['price'].str.replace(',', '').str.extract('(\d+)').astype(float)

# Clean and convert interior_surface and land_surface columns
df['interior_surface_cleaned'] = df['interior_surface'].str.replace(r'\D', '', regex=True)
df['land_surface_cleaned'] = df['land_surface'].str.replace(r'\D', '', regex=True)

# Convert to numeric
df['interior_surface_cleaned'] = pd.to_numeric(df['interior_surface_cleaned'], errors='coerce')
df['land_surface_cleaned'] = pd.to_numeric(df['land_surface_cleaned'], errors='coerce')

# Print out to check
print(df[['interior_surface_cleaned', 'land_surface_cleaned']].head())

# Clean DataFrame by dropping rows with NaN prices, interior_surface, or land_surface
df_cleaned = df.dropna(subset=['price', 'interior_surface_cleaned', 'land_surface_cleaned'])

# Filter for Beachfront and non-Beachfront properties with similar interior_surface and land_surface
# Define criteria for similar surfaces
interior_surface_threshold = 0  # Example threshold for interior surface similarity
land_surface_threshold = 0  # Example threshold for land surface similarity

beachfront_properties = df_cleaned[(df_cleaned['description'].str.contains('Beachfront', na=False)) &
                                   (df_cleaned['interior_surface_cleaned'].ge(interior_surface_threshold)) &
                                   (df_cleaned['land_surface_cleaned'].ge(land_surface_threshold))]

non_beachfront_properties = df_cleaned[(~df_cleaned['description'].str.contains('Beachfront', na=False)) &
                                       (df_cleaned['interior_surface_cleaned'].ge(interior_surface_threshold)) &
                                       (df_cleaned['land_surface_cleaned'].ge(land_surface_threshold))]

# Calculate average prices, handling NaN values
average_beachfront_price = beachfront_properties['price'].mean(skipna=True)
average_non_beachfront_price = non_beachfront_properties['price'].mean(skipna=True)

# Check if average prices are valid numbers
if pd.notna(average_beachfront_price) and pd.notna(average_non_beachfront_price):
    # Create a bar chart to visualize the comparison
    labels = ['Beachfront', 'Non-Beachfront']
    average_prices = [average_beachfront_price, average_non_beachfront_price]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, average_prices, color=['blue', 'green'])
    plt.xlabel('Property Type')
    plt.ylabel('Average Price (Rs)')
    plt.title('Average Price Comparison: Beachfront vs. Non-Beachfront Properties with Similar Surfaces')

    # Display the values on top of each bar
    for i, price in enumerate(average_prices):
        plt.text(i, price + max(average_prices) * 0.01, f'Rs {price:,.2f}', ha='center', va='bottom', fontsize=12)

    plt.grid(True, axis='y')
    plt.ylim(0, max(average_prices) * 1.1)  # Adjust ylim for better visualization

    plt.show()
else:
    print("Unable to plot: Average prices contain NaN or Inf values.")
