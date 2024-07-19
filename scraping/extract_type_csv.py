import pandas as pd

# Load the CSV data
df = pd.read_csv("cleaned_properties.csv")

# Add an ID column
df.insert(0, 'ID', range(1, 1 + len(df)))

# Function to extract type from title
def extract_type(title):
    if isinstance(title, str):
        return title.split(' - ')[0]
    return "Unknown"

# Apply the function to create the 'type' column
df['type'] = df['title'].apply(extract_type)

# Save the modified DataFrame to a new CSV
df.to_csv("cleaned_properties_with_type.csv", index=False)

print("ID column added and type extracted successfully!")
