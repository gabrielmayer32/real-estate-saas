import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error
import joblib
import psycopg2

def clean_surface_area(value):
    if isinstance(value, str):
        value = re.sub(r'[^0-9.]', '', value)  # Remove non-numeric characters
    try:
        return float(value)
    except ValueError:
        return 0.0

def generate_location_to_region_mapping(data):
    location_to_region = {}
    for location in data['location'].unique():
        if 'West' in location:
            location_to_region[location] = 'West'
        elif 'East' in location:
            location_to_region[location] = 'East'
        elif 'North' in location:
            location_to_region[location] = 'North'
        elif 'South' in location:
            location_to_region[location] = 'South'
        else:
            location_to_region[location] = 'Center'
    return location_to_region

# Load your dataset
data = pd.read_csv('../cleaned_properties.csv')

# Preprocess your data
data['land_surface'] = data['land_surface'].apply(clean_surface_area)
data['interior_surface'] = data['interior_surface'].apply(clean_surface_area)

# Fill missing values for surface areas
data['land_surface'] = data['land_surface'].fillna(data['land_surface'].median())
data['interior_surface'] = data['interior_surface'].fillna(data['interior_surface'].median())

# Fill missing values for other columns
data['bedrooms'] = data['bedrooms'].fillna(data['bedrooms'].median())
data['bathrooms'] = data['bathrooms'].fillna(data['bathrooms'].median())
data['toilets'] = data['toilets'].fillna(data['toilets'].median())
data['aircon'] = data['aircon'].fillna(0)

# Convert 'general_features' and 'description' to strings
data['general_features'] = data['general_features'].astype(str)
data['description'] = data['description'].astype(str)

# Generate location-to-region mapping
location_to_region = generate_location_to_region_mapping(data)

# Map specific locations to regions
data['region'] = data['location'].map(location_to_region)

# Extract distinct general_features and description_features
conn = psycopg2.connect(database="real_estate_db", user="root", password="root", host="localhost", port="")
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT UNNEST(string_to_array(general_features, ', ')) AS general_feature FROM properties_property;")
general_features = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT DISTINCT UNNEST(string_to_array(description, ', ')) AS description_feature FROM properties_property;")
description_features = [row[0] for row in cursor.fetchall()]

conn.close()

# Add binary columns for each general_feature and description_feature
for feature in general_features:
    data[f'general_feature_{feature}'] = data['general_features'].apply(lambda x: 1 if feature in x else 0)

for feature in description_features:
    data[f'description_feature_{feature}'] = data['description'].apply(lambda x: 1 if feature in x else 0)

# Add interaction feature for private pool and beachfront
data['interaction_private_pool_beachfront'] = data.apply(lambda row: 1 if row['description_feature_Private pool'] == 1 and row['description_feature_Beachfront'] == 1 else 0, axis=1)

# Step 2: Add polynomial features for interior and land surface
data['interior_surface_squared'] = data['interior_surface'] ** 2
data['land_surface_squared'] = data['land_surface'] ** 2

# Function to train and save model for each property type
def train_and_save_model(property_type):
    subset = data[data['type'] == property_type]
    
    # Select features and target variable
    features = subset[['region', 'interior_surface', 'land_surface', 'interior_surface_squared', 'land_surface_squared', 'bedrooms', 'bathrooms', 'toilets', 'aircon'] + 
                      [f'general_feature_{feature}' for feature in general_features] + 
                      [f'description_feature_{feature}' for feature in description_features] + 
                      ['interaction_private_pool_beachfront']]
    target = subset['price']

    # Convert categorical features to numerical
    features = pd.get_dummies(features, columns=['region'])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

    # Create a pipeline
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestRegressor())
    ])

    # Train the model with cross-validation
    param_grid = {
        'model__n_estimators': [100, 200, 300],
        'model__max_depth': [None, 10, 20, 30],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4]
    }

    grid_search = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)

    # Evaluate the model
    predictions = grid_search.predict(X_test)
    print(f'{property_type} - Mean Absolute Error:', mean_absolute_error(y_test, predictions))

    # Save the trained model and components to disk
    joblib.dump(grid_search.best_estimator_, f'valuation_model_{property_type.replace("/", "_")}.pkl')
    joblib.dump(features.columns.tolist(), f'feature_names_{property_type.replace("/", "_")}.pkl')

# Train and save models for each property type
property_types = ['House / Villa', 'Apartment', 'Penthouse', 'Townhouse / Duplex']
for property_type in property_types:
    train_and_save_model(property_type)


# import pandas as pd
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.preprocessing import StandardScaler
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import mean_absolute_error
# from sklearn.feature_extraction.text import TfidfVectorizer
# import joblib
# import psycopg2
# import re
# import pandas as pd
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.preprocessing import StandardScaler
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import mean_absolute_error
# import joblib
# import re

# import pandas as pd
# import re

# def clean_surface_area(value):
#     if isinstance(value, str):
#         value = re.sub(r'[^0-9.]', '', value)  # Remove non-numeric characters
#     try:
#         return float(value)
#     except ValueError:
#         return 0.0

# def generate_location_to_region_mapping(data):
#     location_to_region = {}
#     for location in data['location'].unique():
#         if 'West' in location:
#             location_to_region[location] = 'West'
#         elif 'East' in location:
#             location_to_region[location] = 'East'
#         elif 'North' in location:
#             location_to_region[location] = 'North'
#         elif 'South' in location:
#             location_to_region[location] = 'South'
#         else:
#             location_to_region[location] = 'Center'
#     return location_to_region

# # Load your dataset
# data = pd.read_csv('../cleaned_properties.csv')

# # Preprocess your data
# data['land_surface'] = data['land_surface'].apply(clean_surface_area)
# data['interior_surface'] = data['interior_surface'].apply(clean_surface_area)

# # Fill missing values for surface areas
# data['land_surface'] = data['land_surface'].fillna(data['land_surface'].median())
# data['interior_surface'] = data['interior_surface'].fillna(data['interior_surface'].median())

# # Fill missing values for other columns
# data['bedrooms'] = data['bedrooms'].fillna(data['bedrooms'].median())
# data['bathrooms'] = data['bathrooms'].fillna(data['bathrooms'].median())
# data['toilets'] = data['toilets'].fillna(data['toilets'].median())
# data['aircon'] = data['aircon'].fillna(0)

# # Convert 'general_features' and 'description' to strings
# data['general_features'] = data['general_features'].astype(str)
# data['description'] = data['description'].astype(str)

# # Generate location-to-region mapping
# location_to_region = generate_location_to_region_mapping(data)

# # Map specific locations to regions
# data['region'] = data['location'].map(location_to_region)

# # Extract distinct general_features and description_features
# import psycopg2

# conn = psycopg2.connect(database="real_estate_db", user="root", password="root", host="localhost", port="")
# cursor = conn.cursor()

# cursor.execute("SELECT DISTINCT UNNEST(string_to_array(general_features, ', ')) AS general_feature FROM properties_property;")
# general_features = [row[0] for row in cursor.fetchall()]

# cursor.execute("SELECT DISTINCT UNNEST(string_to_array(description, ', ')) AS description_feature FROM properties_property;")
# description_features = [row[0] for row in cursor.fetchall()]

# conn.close()

# # Add binary columns for each general_feature and description_feature
# for feature in general_features:
#     data[f'general_feature_{feature}'] = data['general_features'].apply(lambda x: 1 if feature in x else 0)

# for feature in description_features:
#     data[f'description_feature_{feature}'] = data['description'].apply(lambda x: 1 if feature in x else 0)

# # Add interaction feature for private pool and beachfront
# data['interaction_private_pool_beachfront'] = data.apply(lambda row: 1 if row['description_feature_Private pool'] == 1 and row['description_feature_Beachfront'] == 1 else 0, axis=1)

# # Function to train and save model for each property type
# def train_and_save_model(property_type):
#     subset = data[data['type'] == property_type]
    
#     # Select features and target variable
#     features = subset[['region', 'interior_surface', 'land_surface', 'bedrooms', 'bathrooms', 'toilets', 'aircon'] + 
#                       [f'general_feature_{feature}' for feature in general_features] + 
#                       [f'description_feature_{feature}' for feature in description_features] + 
#                       ['interaction_private_pool_beachfront']]
#     target = subset['price']

#     # Convert categorical features to numerical
#     features = pd.get_dummies(features, columns=['region'])

#     # Split the data into training and testing sets
#     X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

#     # Create a pipeline
#     pipeline = Pipeline([
#         ('scaler', StandardScaler()),
#         ('model', RandomForestRegressor())
#     ])

#     # Train the model with cross-validation
#     param_grid = {
#         'model__n_estimators': [100, 200, 300],
#         'model__max_depth': [None, 10, 20, 30],
#         'model__min_samples_split': [2, 5, 10],
#         'model__min_samples_leaf': [1, 2, 4]
#     }

#     grid_search = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, verbose=2)
#     grid_search.fit(X_train, y_train)

#     # Evaluate the model
#     predictions = grid_search.predict(X_test)
#     print(f'{property_type} - Mean Absolute Error:', mean_absolute_error(y_test, predictions))

#     # Save the trained model and components to disk
#     joblib.dump(grid_search.best_estimator_, f'valuation_model_{property_type.replace("/", "_")}.pkl')
#     joblib.dump(features.columns.tolist(), f'feature_names_{property_type.replace("/", "_")}.pkl')

# # Train and save models for each property type
# property_types = ['House / Villa', 'Apartment', 'Penthouse', 'Townhouse / Duplex']
# for property_type in property_types:
#     train_and_save_model(property_type)




# import pandas as pd
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.preprocessing import StandardScaler
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import mean_absolute_error
# from sklearn.feature_extraction.text import TfidfVectorizer
# import joblib
# import psycopg2
# import re

# def clean_surface_area(value):
#     if isinstance(value, str):
#         value = re.sub(r'[^0-9.]', '', value)  # Remove non-numeric characters
#     try:
#         return float(value)
#     except ValueError:
#         return 0.0

# # Load your dataset
# data = pd.read_csv('../cleaned_properties.csv')

# # Preprocess your data
# data['land_surface'] = data['land_surface'].apply(clean_surface_area)
# data['interior_surface'] = data['interior_surface'].apply(clean_surface_area)

# # Fill missing values for surface areas
# data['land_surface'] = data['land_surface'].fillna(data['land_surface'].median())
# data['interior_surface'] = data['interior_surface'].fillna(data['interior_surface'].median())

# # Fill missing values for other columns
# data['bedrooms'] = data['bedrooms'].fillna(data['bedrooms'].median())
# data['bathrooms'] = data['bathrooms'].fillna(data['bathrooms'].median())
# data['toilets'] = data['toilets'].fillna(data['toilets'].median())
# data['aircon'] = data['aircon'].fillna(0)

# # Convert 'general_features' and 'description' to strings
# data['general_features'] = data['general_features'].astype(str)
# data['description'] = data['description'].astype(str)

# # Extract distinct general_features
# conn = psycopg2.connect(database="real_estate_db", user="root", password="root", host="localhost", port="")
# cursor = conn.cursor()

# cursor.execute("SELECT DISTINCT UNNEST(string_to_array(general_features, ', ')) AS general_feature FROM properties_property;")
# general_features = [row[0] for row in cursor.fetchall()]

# cursor.execute("SELECT DISTINCT UNNEST(string_to_array(description, ', ')) AS description_feature FROM properties_property;")
# description_features = [row[0] for row in cursor.fetchall()]

# conn.close()

# # Add binary columns for each general_feature and description_feature
# for feature in general_features:
#     data[f'general_feature_{feature}'] = data['general_features'].apply(lambda x: 1 if feature in x else 0)

# for feature in description_features:
#     data[f'description_feature_{feature}'] = data['description'].apply(lambda x: 1 if feature in x else 0)

# # Select features and target variable
# features = data[['type', 'location', 'interior_surface', 'land_surface', 'bedrooms', 'bathrooms', 'toilets', 'aircon'] + 
#                 [f'general_feature_{feature}' for feature in general_features] + 
#                 [f'description_feature_{feature}' for feature in description_features]]
# target = data['price']

# # Convert categorical features to numerical
# features = pd.get_dummies(features, columns=['type', 'location'])

# # Split the data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# # Create a pipeline
# pipeline = Pipeline([
#     ('scaler', StandardScaler()),
#     ('model', RandomForestRegressor())
# ])

# # Train the model with cross-validation
# param_grid = {
#     'model__n_estimators': [100, 200],
#     'model__max_depth': [None, 10, 20],
#     'model__min_samples_split': [2, 5, 10],
#     'model__min_samples_leaf': [1, 2, 4]
# }

# grid_search = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, verbose=2)
# grid_search.fit(X_train, y_train)

# # Evaluate the model
# predictions = grid_search.predict(X_test)
# print('Mean Absolute Error:', mean_absolute_error(y_test, predictions))

# # Save the trained model and components to disk
# joblib.dump(grid_search.best_estimator_, 'valuation_model.pkl')
# joblib.dump(features.columns.tolist(), 'feature_names.pkl')
