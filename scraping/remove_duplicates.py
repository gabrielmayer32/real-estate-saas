import pandas as pd

# Load the CSV data
df = pd.read_csv('./test_new_db.csv')

# Display the first few rows to inspect the data
print("Original data:")
print(df.head())

# Check for NaN values in the dataframe
nan_summary = df.isna().sum()
print("NaN summary:")
print(nan_summary)

# Drop duplicates
df.drop_duplicates(inplace=True)

# Drop rows where the 'ref' column is NaN
df = df[df['ref'].notna()]

# Optionally, drop rows where other critical columns are NaN
critical_columns = ['title', 'location', 'price', 'details_link', 'ref']
df.dropna(subset=critical_columns, inplace=True)

# Clean the 'price' field
def clean_price(price):
    if pd.isna(price):
        return None
    price = str(price).replace('Rs', '').replace(',', '').strip()
    try:
        return float(price)
    except ValueError:
        return None

df['price'] = df['price'].apply(clean_price)

# Convert numeric fields to integers where necessary
def convert_to_int(value):
    if pd.isna(value) or value == '':
        return None
    try:
        return int(float(value))
    except ValueError:
        return None

numeric_fields = ['bedrooms', 'bathrooms', 'toilets']
for field in numeric_fields:
    df[field] = df[field].apply(convert_to_int)

# Drop rows where the 'price' field could not be converted
df.dropna(subset=['price'], inplace=True)

# Save the cleaned data to a new CSV file
df.to_csv('cleaned_properties.csv', index=False)

print(f"Number of rows after cleaning: {len(df)}")

# Load and display the cleaned data
cleaned_df = pd.read_csv('cleaned_properties.csv')
print("Cleaned data:")
print(cleaned_df.head())
