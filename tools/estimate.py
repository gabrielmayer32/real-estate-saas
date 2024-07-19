import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import os

def process_data(property_type):
    # Function to clean the price column
    def clean_price(price):
        if isinstance(price, str):
            # Remove non-numeric characters
            clean_price = re.sub(r'[^\d.]', '', price)
            return float(clean_price) if clean_price else None
        return price

    # Load the CSV data into a DataFrame
    df = pd.read_csv('properties.csv')

    # Display the first few rows of the DataFrame
    print("Original DataFrame:")
    print(df.head())

    # Filter the data based on property type
    df = df[df['type'] == property_type]

    # Check if data is filtered correctly
    print(f"\nFiltered DataFrame for {property_type}:")
    print(df.head())

    # Clean the price column
    df['price'] = df['price'].apply(clean_price)

    # Convert 'no room' and 'size (m²)' columns to numeric
    df['no room'] = pd.to_numeric(df['no room'], errors='coerce')
    df['size (m²)'] = pd.to_numeric(df['size (m²)'], errors='coerce')

    # Check if price column is cleaned correctly
    print("\nPrice column after cleaning:")
    print(df['price'].head())

    # Fill NaN values in numeric columns with 0
    df['price'].fillna(0, inplace=True)
    df['no room'].fillna(0, inplace=True)
    df['size (m²)'].fillna(0, inplace=True)

    # Check if NaN values are filled
    print("\nDataFrame after filling NaN values:")
    print(df.head())

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Remove outliers - you may adjust the thresholds based on your dataset
    df = df[(df['price'] < 1e8) & (df['size (m²)'] < 10000)]

    # Check if outliers are removed
    print("\nDataFrame after removing outliers:")
    print(df.describe())

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

    # Price distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['price'], bins=50, kde=True)
    plt.title(f'Price Distribution for {property_type}')
    plt.xlabel('Price (Rs)')
    plt.ylabel('Frequency')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(currency_formatter))
    plt.savefig(f'price_distribution_{safe_property_type}.png')
    plt.show()

    # Size vs. Price
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='size (m²)', y='price', data=df)
    plt.title(f'Size vs. Price for {property_type}')
    plt.xlabel('Size (m²)')
    plt.ylabel('Price (Rs)')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(size_formatter))
    plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))

    # Set the limits to focus the view
    plt.xlim(0, df['size (m²)'].max())
    plt.ylim(0, df['price'].max())
    plt.savefig(f'size_vs_price_{safe_property_type}.png')
    plt.show()

    # Bedrooms vs. Price
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='no room', y='price', data=df)
    plt.title(f'Bedrooms vs. Price for {property_type}')
    plt.xlabel('Number of Bedrooms')
    plt.ylabel('Price (Rs)')
    plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))
    plt.savefig(f'bedrooms_vs_price_{safe_property_type}.png')
    plt.show()

# Get the property type from the user
property_type = input("Enter the property type to filter (e.g., 'House / Villa', 'Apartment', etc.): ")

# Run the process_data function with the chosen property type
process_data(property_type)
