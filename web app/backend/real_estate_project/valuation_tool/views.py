# views.py in valuation_tool

from django.http import JsonResponse
from rest_framework.views import APIView
import joblib
import pandas as pd
import psycopg2

class ValuationView(APIView):
    def post(self, request):
        # Load the trained model and scaler
        model = joblib.load('../valuation_model.pkl')
        scaler = joblib.load('../scaler.pkl')
        
        # Extract property features from the request
        features = request.data
        df = pd.DataFrame([features])
        df = pd.get_dummies(df)
        
        # Extract distinct general_features and indoor_features
        conn = psycopg2.connect(database="your_database", user="your_user", password="your_password", host="your_host", port="your_port")
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT UNNEST(string_to_array(general_features, ', ')) AS general_feature FROM properties_property;")
        general_features = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT UNNEST(string_to_array(indoor_features, ', ')) AS indoor_feature FROM properties_property;")
        indoor_features = [row[0] for row in cursor.fetchall()]

        conn.close()

        # Ensure the DataFrame has the same columns as the training set
        for col in model.feature_names_in_:
            if col not in df.columns:
                df[col] = 0

        # Scale the features
        df = scaler.transform(df)
        
        # Predict the price
        prediction = model.predict(df)
        
        return JsonResponse({'predicted_price': prediction[0]})

import joblib
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import pandas as pd
import re

def clean_surface_area(value):
    if isinstance(value, str):
        value = re.sub(r'[^0-9.]', '', value)  # Remove non-numeric characters
    try:
        return float(value)
    except ValueError:
        return 0.0

def clean_surface_area(value):
    if isinstance(value, str):
        value = re.sub(r'[^0-9.]', '', value)  # Remove non-numeric characters
    try:
        return float(value)
    except ValueError:
        return 0.0
    
class ValuationPredictionView(APIView):
    def post(self, request):
        try:
            property_type = request.data.get('type', '').replace('/', '_')
            model_path = os.path.join(settings.BASE_DIR, f'./valuation_tool/valuation_model_{property_type}.pkl')
            feature_names_path = os.path.join(settings.BASE_DIR, f'./valuation_tool/feature_names_{property_type}.pkl')

            model = joblib.load(model_path)
            feature_names = joblib.load(feature_names_path)

            # Log the incoming data for debugging
            print("Request data:", request.data)

            # Extract base features from request data
            features = {
                'region': request.data.get('region', ''),
                'interior_surface': clean_surface_area(request.data.get('interior_surface', 0)),
                'land_surface': clean_surface_area(request.data.get('land_surface', 0)),
                'interior_surface_squared': clean_surface_area(request.data.get('interior_surface', 0)) ** 2,
                'land_surface_squared': clean_surface_area(request.data.get('land_surface', 0)) ** 2,
                'bedrooms': int(request.data.get('bedrooms', 0)),
                'bathrooms': int(request.data.get('bathrooms', 0)),
                'toilets': int(request.data.get('toilets', 0)),
                'aircon': int(request.data.get('aircon', 0))
            }

            # Add general features
            general_features_list = request.data.get('general_features', [])
            for feature in feature_names:
                if feature.startswith('general_feature_'):
                    features[feature] = 1 if feature[len('general_feature_'):] in general_features_list else 0

            # Add description features
            description_features_list = request.data.get('description', '').split(', ')
            for feature in feature_names:
                if feature.startswith('description_feature_'):
                    features[feature] = 1 if feature[len('description_feature_'):] in description_features_list else 0

            # Add interaction feature for private pool and beachfront
            features['interaction_private_pool_beachfront'] = 1 if 'Private pool' in description_features_list and 'Beachfront' in description_features_list else 0

            # Create DataFrame for easier manipulation
            df = pd.DataFrame([features])

            # Convert region to dummy variables and ensure all necessary columns are present
            region_dummies = pd.get_dummies(df['region'], prefix='region')
            df = pd.concat([df, region_dummies], axis=1)
            df.drop('region', axis=1, inplace=True)

            # Add missing features with default value (0 or empty string)
            missing_features = list(set(feature_names) - set(df.columns))
            missing_df = pd.DataFrame(0, index=df.index, columns=missing_features)

            # Concatenate the original and missing features DataFrames
            df = pd.concat([df, missing_df], axis=1)

            # Ensure all features are in the correct order
            df = df[feature_names]

            # Make prediction using the pipeline
            prediction = model.predict(df)

            # Ensure that the price does not decrease with increasing interior or land surface area
            for feature in ['interior_surface', 'land_surface']:
                if features[feature] > request.data.get(feature, 0):
                    prediction[0] = max(prediction[0], model.predict(pd.DataFrame([features]))[0])

            return Response({'predicted_price': prediction[0]}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class ValuationPredictionView(APIView):
#     def post(self, request):
#         try:
#             property_type = request.data.get('type', '').replace('/', '_')
#             model_path = os.path.join(settings.BASE_DIR, f'./valuation_tool/valuation_model_{property_type}.pkl')
#             feature_names_path = os.path.join(settings.BASE_DIR, f'./valuation_tool/feature_names_{property_type}.pkl')

#             model = joblib.load(model_path)
#             feature_names = joblib.load(feature_names_path)

#             # Log the incoming data for debugging
#             print("Request data:", request.data)

#             # Extract base features from request data
#             features = {
#                 'region': request.data.get('region', ''),
#                 'interior_surface': clean_surface_area(request.data.get('interior_surface', 0)),
#                 'land_surface': clean_surface_area(request.data.get('land_surface', 0)),
#                 'bedrooms': int(request.data.get('bedrooms', 0)),
#                 'bathrooms': int(request.data.get('bathrooms', 0)),
#                 'toilets': int(request.data.get('toilets', 0)),
#                 'aircon': int(request.data.get('aircon', 0))
#             }

#             # Add general features
#             general_features_list = request.data.get('general_features', [])
#             for feature in feature_names:
#                 if feature.startswith('general_feature_'):
#                     features[feature] = 1 if feature[len('general_feature_'):] in general_features_list else 0

#             # Add description features
#             description_features_list = request.data.get('description', '').split(', ')
#             for feature in feature_names:
#                 if feature.startswith('description_feature_'):
#                     features[feature] = 1 if feature[len('description_feature_'):] in description_features_list else 0

#             # Add interaction feature for private pool and beachfront
#             features['interaction_private_pool_beachfront'] = 1 if 'Private pool' in description_features_list and 'Beachfront' in description_features_list else 0

#             # Create DataFrame for easier manipulation
#             df = pd.DataFrame([features])

#             # Convert region to dummy variables and ensure all necessary columns are present
#             region_dummies = pd.get_dummies(df['region'], prefix='region')
#             df = pd.concat([df, region_dummies], axis=1)
#             df.drop('region', axis=1, inplace=True)

#             # Add missing features with default value (0 or empty string)
#             missing_features = list(set(feature_names) - set(df.columns))
#             missing_df = pd.DataFrame(0, index=df.index, columns=missing_features)

#             # Concatenate the original and missing features DataFrames
#             df = pd.concat([df, missing_df], axis=1)

#             # Ensure all features are in the correct order
#             df = df[feature_names]

#             # Make prediction using the pipeline
#             prediction = model.predict(df)
#             return Response({'predicted_price': prediction[0]}, status=status.HTTP_200_OK)
#         except Exception as e:
#             print("Error:", str(e))
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import psycopg2

# class DistinctFeaturesView(APIView):
#     def get(self, request):
#         try:
#             conn = psycopg2.connect(database="real_estate_db", user="root", password="root", host="localhost", port="")
#             cursor = conn.cursor()

#             cursor.execute("SELECT DISTINCT UNNEST(string_to_array(general_features, ', ')) AS general_feature FROM properties_property;")
#             general_features = [row[0] for row in cursor.fetchall()]

#             cursor.execute("SELECT DISTINCT type FROM properties_property;")
#             property_types = [row[0] for row in cursor.fetchall()]

#             cursor.execute("SELECT DISTINCT location FROM properties_property;")
#             locations = [row[0] for row in cursor.fetchall()]

#             conn.close()

#             return Response({
#                 'general_features': general_features,
#                 'property_types': property_types,
#                 'locations': locations,
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DistinctFeaturesView(APIView):
    def get(self, request):
        try:
            conn = psycopg2.connect(database="real_estate_db", user="root", password="root", host="localhost", port="")
            cursor = conn.cursor()

            # Extract and split description features into distinct terms
            cursor.execute("SELECT description FROM properties_property;")
            description_features = set()
            for row in cursor.fetchall():
                if row[0]:  # Check if the row is not empty
                    features = [feature.strip() for feature in row[0].split(',')]
                    description_features.update(features)
            description_features = sorted(description_features)

            # Extract and split general features into distinct terms
            cursor.execute("SELECT general_features FROM properties_property;")
            general_features = set()
            for row in cursor.fetchall():
                if row[0]:  # Check if the row is not empty
                    features = [feature.strip() for feature in row[0].split(',')]
                    general_features.update(features)
            general_features = sorted(general_features)

            # Extract distinct property types
            cursor.execute("SELECT DISTINCT type FROM properties_property;")
            property_types = sorted(set(row[0] for row in cursor.fetchall() if row[0]))

            # Extract distinct locations
            cursor.execute("SELECT DISTINCT location FROM properties_property;")
            locations = sorted(set(row[0] for row in cursor.fetchall() if row[0]))

            conn.close()

            # Map locations to regions
            regions = sorted(set(map_location_to_region(location) for location in locations))

            return Response({
                'description_features': description_features,
                'general_features': general_features,
                'property_types': property_types,
                'locations': locations,
                'regions': regions
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def map_location_to_region(location):
    if 'West' in location:
        return 'West'
    elif 'East' in location:
        return 'East'
    elif 'North' in location:
        return 'North'
    elif 'South' in location:
        return 'South'
    else:
        return 'Center'