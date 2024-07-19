import pandas as pd
import psycopg2
from psycopg2 import sql
from datetime import datetime

# Database connection parameters
DATABASE = "real_estate_db"
USER = "root"
PASSWORD = "root"
HOST = "localhost"
PORT = ""

# Read the CSV file
csv_file_path = '/Users/gabrielmayer/Desktop/real estate micro Saas/web app/backend/real_estate_project/properties/management/commands/cleaned_properties_1.csv'
data = pd.read_csv(csv_file_path)

# Clean the price column
data['price'] = pd.to_numeric(data['price'], errors='coerce')

# Filter out rows with invalid prices
data = data.dropna(subset=['price'])

# Convert 'ref' to string, strip leading/trailing whitespaces, and remove .0
data['ref'] = data['ref'].astype(str).str.strip().str.replace('.0$', '', regex=True)

# Define the target date for the price history records
target_date = datetime(2024, 6, 28)

# Establish a database connection
conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
cursor = conn.cursor()

# Loop through the data and insert price history records
for index, row in data.iterrows():
    property_ref = row['ref']
    price = row['price']
    
    # Log the property_ref for debugging
    print(f"Looking up property with ref: {property_ref}")
    
    # Find the corresponding property ID
    cursor.execute(sql.SQL("SELECT id FROM properties_property WHERE ref = %s"), [property_ref])
    property_id = cursor.fetchone()
    
    # Log the result of the database query
    if property_id:
        print(f"Found property ID: {property_id[0]}")
    else:
        print(f"No property found with ref: {property_ref}")
    
    if property_id:
        property_id = property_id[0]
        
        # Insert the price history record
        cursor.execute(sql.SQL("""
            INSERT INTO properties_propertypricehistory (property_id, price, date)
            VALUES (%s, %s, %s)
        """), [property_id, price, target_date])

# Commit the transaction
conn.commit()

# Close the database connection
cursor.close()
conn.close()

print("Price history records imported successfully.")
