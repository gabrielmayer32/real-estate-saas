import pandas as pd
import matplotlib.pyplot as plt



df = pd.read_csv('Land undervalued by region - real_estate_listings_modified.csv')
# Example data loading check:
print("Initial DataFrame:")
print(df.head())

# Clean and convert price column
df['price'] = df['price'].str.replace(',', '').str.extract('(\d+)').astype(float)

# Clean DataFrame by dropping rows with NaN prices
df_cleaned = df.dropna(subset=['price'])

# Filter for Beachfront and non-Beachfront properties in the West region
# beachfront_properties = df_cleaned[(df_cleaned['description'].str.contains('Beachfront') | df_cleaned['description'].str.contains('Sea access'))]
# non_beachfront_properties = df_cleaned[~(df_cleaned['description'].str.contains('Beachfront') | df_cleaned['description'].str.contains('Sea access'))]

beachfront_properties = df_cleaned[df_cleaned['description'].str.contains('Beachfront', na=False)]
non_beachfront_properties = df_cleaned[~df_cleaned['description'].str.contains('Beachfront', na=False)]

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
    plt.title('Average Price Comparison: Beachfront vs. Non-Beachfront Properties')

    # Display the values on top of each bar
    for i, price in enumerate(average_prices):
        plt.text(i, price + max(average_prices) * 0.01, f'Rs {price:,.2f}', ha='center', va='bottom', fontsize=12)

    plt.grid(True, axis='y')
    plt.ylim(0, max(average_prices) * 1.1)  # Adjust ylim for better visualization

    plt.show()
else:
    print("Unable to plot: Average prices contain NaN or Inf values.")