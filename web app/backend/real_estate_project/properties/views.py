from rest_framework import viewsets
from .models import Agency, Property, PricePerSquareMeter, Region
from .serializers import PropertySerializer, PricePerSquareMeterSerializer, RegionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Property
from django.db import models  # Import models from django.db

class CurrentMarketValueView(APIView):
    def get(self, request):
        total_market_value = Property.objects.filter(sold=False).aggregate(total_value=Sum('price'))['total_value']
        return Response({'current_market_value': total_market_value}, status=status.HTTP_200_OK)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(sold=False)
    serializer_class = PropertySerializer

class PricePerSquareMeterViewSet(viewsets.ModelViewSet):
    queryset = PricePerSquareMeter.objects.all()
    serializer_class = PricePerSquareMeterSerializer

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

import re


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PricePerSquareMeter, Property, Region
from django.db.models import Avg, Sum, F, FloatField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, FloatField
from properties.models import Property
from django.db.models.functions import Cast
from django.db.models import FloatField, Q



class PricePerSquareMeterView(APIView):
    def get(self, request):
        property_type = request.GET.get('property_type')
        region = request.GET.get('region')
        print(f"Requested property_type: {property_type}, region: {region}")

        if not property_type or not region:
            return Response({'error': 'property_type and region are required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        if "Land" in property_type:
            surface_field = 'land_surface'
        else:
            surface_field = 'interior_surface'

        filter_conditions = Q(title__icontains=property_type) & Q(sold=False) & ~Q(**{surface_field: None})

        if region != "All":
            filter_conditions &= Q(location__icontains=region)

        valid_properties = Property.objects.filter(filter_conditions)
        print(f"Valid properties: {valid_properties.count()}")

        # Convert and clean non-numeric characters
        def clean_surface(value):
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point
                cleaned_value = re.sub(r'[^\d.]+', '', value)
                return float(cleaned_value) if cleaned_value else None
            return value

        # Apply cleaning in annotation
        valid_properties = valid_properties.annotate(
            numeric_surface=Cast(
                F(surface_field),
                output_field=FloatField()
            )
        )

        # Ensure the numeric_surface is not None
        valid_properties = valid_properties.exclude(numeric_surface__isnull=True)

        try:
            price_data = valid_properties.aggregate(
                total_price=Sum('price', output_field=FloatField()),
                total_surface=Sum('numeric_surface', output_field=FloatField())
            )

            if price_data['total_surface'] and price_data['total_surface'] > 0:
                average_price = price_data['total_price'] / price_data['total_surface']
                return Response({
                    'property_type': property_type,
                    'region': region if region != "All" else "All",
                    'price_per_square_meter': average_price
                }, status=status.HTTP_200_OK)

            return Response({'error': 'No valid data found for the specified parameters'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error processing data: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class PricePerSquareMeterView(APIView):
#     def get(self, request):
#         property_type = request.GET.get('property_type')
#         region = request.GET.get('region')
#         print(property_type, region)

#         if not property_type or not region:
#             return Response({'error': 'property_type and region are required parameters'}, status=status.HTTP_400_BAD_REQUEST)

#         if region == "All":
#             price_data = Property.objects.filter(title__icontains=property_type).aggregate(
#                 total_price=Sum('price', output_field=FloatField()),
#                 total_surface=Sum('interior_surface', output_field=FloatField())
#             )
#             if price_data['total_surface'] > 0:
#                 average_price = price_data['total_price'] / price_data['total_surface']
#                 return Response({
#                     'property_type': property_type,
#                     'region': 'All',
#                     'price_per_square_meter': average_price
#                 }, status=status.HTTP_200_OK)
#         else:
#             price_data = Property.objects.filter(title__icontains=property_type, location__icontains=region).aggregate(
#                 total_price=Sum('price', output_field=FloatField()),
#                 total_surface=Sum('interior_surface', output_field=FloatField())
#             )
#             if price_data['total_surface'] > 0:
#                 average_price = price_data['total_price'] / price_data['total_surface']
#                 return Response({
#                     'property_type': property_type,
#                     'region': region,
#                     'price_per_square_meter': average_price
#                 }, status=status.HTTP_200_OK)
        
#         return Response({'error': 'Data not found for the given property_type and region'}, status=status.HTTP_404_NOT_FOUND)

import numpy as np


class PriceDistributionView(APIView):
    def get(self, request):
        property_type = request.GET.get('property_type')
        region = request.GET.get('region')
        location = request.GET.get('location')  

        filter_conditions = Q(sold=False)  # Exclude sold properties

        if property_type and property_type != 'All':
            filter_conditions &= Q(type__icontains=property_type)
        if region and region != 'All':
            filter_conditions &= Q(region__name__icontains=region)
        if location:
            filter_conditions &= Q(location__icontains=location)
        
        print(filter_conditions)
        properties = Property.objects.filter(filter_conditions)
        print(properties.count())
        prices = properties.values_list('price', flat=True)
        prices = [float(price) for price in prices if price]

        if not prices:
            return Response({'error': 'No data available for the given property_type, region, and location'}, status=status.HTTP_404_NOT_FOUND)

        # Define custom bins for better distribution
        bins = [0, 5000000, 10000000, 20000000, 25000000, 50000000, 75000000, 100000000, 150000000, 200000000, 250000000, 500000000, 750000000, 1000000000]

        # Ensure max_price is added to the bins if it's greater than the largest predefined bin
        max_price = max(prices)
        if max_price > bins[-1]:
            bins.append(max_price + 1)

        hist, bin_edges = np.histogram(prices, bins=bins)

        price_distribution = {
            'bin_edges': bin_edges.tolist(),
            'counts': hist.tolist()
        }

        return Response(price_distribution, status=status.HTTP_200_OK)

    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from properties.models import Location
from properties.serializers import LocationSerializer

from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class LocationHeatmapView(APIView):
    def get(self, request):
        locations = Location.objects.all()
        location_data = []
        for location in locations:
            locationName = location.name + ", " + location.region
            # Calculate the average price for properties at this location
            avg_price = Property.objects.filter(location=locationName).aggregate(Avg('price'))['price__avg']
            location_data.append({
                'name': location.name,
                'region': location.region,
                'latitude': location.latitude,
                'longitude': location.longitude,
                'average_price': avg_price
            })
        return Response(location_data, status=status.HTTP_200_OK)

# In exchange_rates/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from properties.models import ExchangeRate



class ExchangeRatesView(APIView):
    def get(self, request):
        rates = ExchangeRate.objects.all()
        data = {rate.currency: rate.rate for rate in rates}
        return Response(data, status=status.HTTP_200_OK)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Property
from django.db.models import Avg, Sum, Count

from django.db.models import Avg, Count, F, FloatField, ExpressionWrapper, Case, When
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from properties.models import Property

class MetricsView(APIView):
    def get(self, request):
        property_type = request.GET.get('property_type')
        region = request.GET.get('region')
        location = request.GET.get('location')  

        filter_conditions = Q(sold=False)  # Exclude sold properties

        if property_type and property_type != 'All':
            filter_conditions &= Q(type__icontains=property_type)

        if region and region != 'All':
            filter_conditions &= Q(region__name__icontains=region)  # Adjusted region filter

        if location:  # Apply location filter if provided
            filter_conditions &= Q(location__icontains=location)

        properties = Property.objects.filter(filter_conditions)
        print(f"Filtered Properties Count: {properties.count()}")
        print(f"Filter Conditions: {filter_conditions}")

        if 'land' in property_type.lower():
            # Calculate price per square meter based on land surface
            price_per_sq_meter = properties.annotate(
                price_per_sq_meter=Case(
                    When(
                        land_surface__gt=0,
                        then=ExpressionWrapper(
                            F('price') / F('land_surface'),
                            output_field=FloatField()
                        )
                    ),
                    default=None,
                    output_field=FloatField()
                )
            ).aggregate(
                avg_price_per_sq_meter=Avg('price_per_sq_meter'),
                avg_land_size=Avg(Cast('land_surface', FloatField())),
                count=Count('id')
            )

            # Rename keys in the response
            metrics = {
                'price_per_sq_meter': price_per_sq_meter['avg_price_per_sq_meter'],
                'average_land_size': price_per_sq_meter['avg_land_size'],
                'count': price_per_sq_meter['count']
            }
            print(f"Metrics for land: {metrics}")

        else:
            # Calculate price per square meter based on interior surface
            price_per_sq_meter = properties.annotate(
                price_per_sq_meter=Case(
                    When(
                        interior_surface__gt=0,
                        then=ExpressionWrapper(
                            F('price') / F('interior_surface'),
                            output_field=FloatField()
                        )
                    ),
                    default=None,
                    output_field=FloatField()
                )
            ).aggregate(
                avg_price_per_sq_meter=Avg('price_per_sq_meter'),
                avg_interior_size=Avg('interior_surface'),
                avg_land_size=Avg(Cast('land_surface', FloatField())),
                count=Count('id')
            )

            # Rename keys in the response
            metrics = {
                'price_per_sq_meter': price_per_sq_meter['avg_price_per_sq_meter'],
                'average_interior_size': price_per_sq_meter['avg_interior_size'],
                'average_land_size': price_per_sq_meter['avg_land_size'],
                'count': price_per_sq_meter['count']
            }
            print(f"Metrics for non-land: {metrics}")

        return Response(metrics, status=status.HTTP_200_OK)


    
from django.http import JsonResponse

def get_agencies(request):
    agencies = Agency.objects.all().values('id', 'name', 'other_fields')
    return JsonResponse(list(agencies), safe=False)


from django.db.models import Count, Sum
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class AgencyRankingView(APIView):
    def get(self, request):
        property_type = request.GET.get('property_type')
        region = request.GET.get('region')
        ranking_by = request.GET.get('ranking_by', 'count')  # Default to ranking by count

        filter_conditions = Q()
        if property_type and property_type != 'All':
            filter_conditions &= Q(type__icontains=property_type)
        if region and region != 'All':
            filter_conditions &= Q(location__icontains=region)

        if ranking_by == 'count':
            agencies = Property.objects.filter(filter_conditions) \
                .values('agency__id', 'agency__name') \
                .annotate(property_count=Count('id')) \
                .order_by('-property_count')
        else:  # ranking_by == 'value'
            agencies = Property.objects.filter(filter_conditions) \
                .values('agency__id', 'agency__name') \
                .annotate(total_value=Sum('price')) \
                .order_by('-total_value')

        if ranking_by == 'count':
            response_data = [
                {
                    'agency_id': agency['agency__id'],
                    'agency_name': agency['agency__name'],
                    'property_count': agency['property_count'],
                    'total_value': Property.objects.filter(agency__id=agency['agency__id']).aggregate(total_value=Sum('price'))['total_value']
                }
                for agency in agencies
            ]
        else:
            response_data = [
                {
                    'agency_id': agency['agency__id'],
                    'agency_name': agency['agency__name'],
                    'property_count': Property.objects.filter(agency__id=agency['agency__id']).count(),
                    'total_value': agency['total_value']
                }
                for agency in agencies
            ]
        
        print(response_data)

        return Response(response_data, status=status.HTTP_200_OK)



from django.db.models import Q, Avg, StdDev
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Avg, StdDev
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Avg, StdDev

from django.db.models import Avg, FloatField, Q, F, Func
from django.db.models.functions import Cast
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Property, Region

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, F, FloatField, Avg, ExpressionWrapper, Case, When
from .models import Property, Region

class InvestmentOpportunitiesView(APIView):
    def get(self, request):
        property_type = request.GET.get('property_type')
        region_name = request.GET.get('region')

        filter_conditions = Q(sold=False)  # Exclude sold properties

        if property_type and property_type != 'All':
            filter_conditions &= Q(type__icontains=property_type)
        if region_name and region_name != 'All':
            try:
                region = Region.objects.get(name__iexact=region_name)
                filter_conditions &= Q(region=region)
            except Region.DoesNotExist:
                return Response({'error': 'Invalid region provided'}, status=status.HTTP_404_NOT_FOUND)

        properties = Property.objects.filter(filter_conditions)

        if not properties.exists():
            return Response({'error': 'No data available for the given filters'}, status=status.HTTP_404_NOT_FOUND)

        # Filter out properties with invalid interior_surface or land_surface values
        valid_properties = []
        for property in properties:
            try:
                interior_surface = float(property.interior_surface) if property.interior_surface else 0.0
                land_surface = float(property.land_surface) if property.land_surface else 0.0

                # Skip Villa properties without land_surface
                if property.type.lower() == 'villa' and land_surface == 0:
                    continue

                if interior_surface >= 0 and land_surface >= 0:
                    valid_properties.append(property)
            except ValueError as e:
                print(f"Invalid surface value for property {property.id}: {e}")

        if not valid_properties:
            return Response({'error': 'No valid properties found after filtering'}, status=status.HTTP_404_NOT_FOUND)

        # Recalculate avg_price_per_sqm using valid_properties
        property_ids = [property.id for property in valid_properties]
        filtered_properties = Property.objects.filter(id__in=property_ids)

        filtered_properties = filtered_properties.annotate(
            total_surface=Cast(F('interior_surface'), FloatField()) + Cast(F('land_surface'), FloatField())
        ).exclude(total_surface=0)

        avg_price_per_sqm = filtered_properties.values('type', 'region').annotate(
            avg_price_per_sqm=Avg(
                Cast(F('price'), FloatField()) / Cast(F('total_surface'), FloatField())
            )
        ).order_by()

        # Merge avg_price_per_sqm back into properties
        avg_price_per_sqm_dict = {(item['type'], item['region']): item['avg_price_per_sqm'] for item in avg_price_per_sqm}

        # Print avg_price_per_sqm_dict for debugging
        print(f"Average Price per SQM: {avg_price_per_sqm_dict}")

        def get_normalized_price(property):
            try:
                price = float(property.price)
                interior_surface = float(property.interior_surface) if property.interior_surface else 0.0
                land_surface = float(property.land_surface) if property.land_surface else 0.0
                total_surface = interior_surface + land_surface

                if total_surface == 0:
                    return None

                normalized_price = price / total_surface
                return normalized_price
            except Exception as e:
                print(f"Error calculating normalized price for property {property.id}: {e}")
                return None

        overvalued_properties = []
        undervalued_properties = []
        for property in valid_properties:
            normalized_price = get_normalized_price(property)
            if normalized_price is not None:
                avg_price_per_sqm = avg_price_per_sqm_dict.get((property.type, property.region_id), None)
                if avg_price_per_sqm:
                    # Print comparison details for debugging
                    print(f"Property {property.id} - Normalized Price: {normalized_price}, Avg Price per SQM: {avg_price_per_sqm}")
                    if normalized_price > avg_price_per_sqm * 1.1:  # 10% above the average
                        overvalued_properties.append(property)
                    elif normalized_price < avg_price_per_sqm * 0.9:  # 10% below the average
                        undervalued_properties.append(property)

        overvalued_data = [{'title': prop.title, 'location': prop.location, 'price': prop.price, 'details_link': prop.details_link} for prop in overvalued_properties]
        undervalued_data = [{'title': prop.title, 'location': prop.location, 'price': prop.price, 'details_link': prop.details_link} for prop in undervalued_properties]

        return Response({
            'overvalued': overvalued_data,
            'undervalued': undervalued_data
        }, status=status.HTTP_200_OK)

    
class PropertyTypeDistributionView(APIView):
    def get(self, request):
        region = request.GET.get('region', 'All')

        filter_conditions = Q(sold=False)  # Exclude sold properties
        if region != 'All':
            filter_conditions &= Q(location__icontains=region)

        properties = Property.objects.filter(filter_conditions)

        if not properties.exists():
            return Response({'error': 'No data available for the given filters'}, status=status.HTTP_404_NOT_FOUND)

        distribution = properties.values('type').annotate(count=Count('id')).order_by('-count')

        data = list(distribution)

        return Response(data, status=status.HTTP_200_OK)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Property
from .serializers import PropertySerializer

class ScatterPlotDataView(APIView):
    def get(self, request):
        currency = request.query_params.get('currency')
        property_type = request.query_params.get('propertyType')
        region = request.query_params.get('region')
        location = request.query_params.get('location')

        properties = Property.objects.filter(sold=False)  # Exclude sold properties

        if property_type and property_type != 'All':
            properties = properties.filter(type=property_type)

        if region and region != 'All':
            properties = properties.filter(region__name=region)

        if location:
            properties = properties.filter(location__icontains=location)

        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# views.py
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Property

class PriceVsAccessibleView(APIView):
    def get(self, request):
        region = request.GET.get('region')
        property_type = request.GET.get('property_type')
        location = request.GET.get('location')
        min_size = request.GET.get('min_size', 0)
        max_size = request.GET.get('max_size', 9999999)

        filter_conditions = Q(sold=False, interior_surface__gte=min_size, interior_surface__lte=max_size)  # Exclude sold properties

        if region and region != 'All':
            filter_conditions &= Q(region__name__icontains=region)
        if location:
            filter_conditions &= Q(location__icontains=location)
        if property_type and property_type != 'All':
            filter_conditions &= Q(type__icontains=property_type)

        properties = Property.objects.filter(filter_conditions)

        if not properties.exists():
            return Response({'error': 'No data available for the given filters'}, status=status.HTTP_404_NOT_FOUND)

        data = list(properties.values(
            'title', 'location', 'price', 'details_link', 'accessible_to_foreigners',
            'interior_surface', 'land_surface', 'type', 'swimming_pool', 'general_features'
        ))

        return Response(data, status=status.HTTP_200_OK)

from django.db.models import Avg, Max, Min, Q
from properties.models import Property
from django.http import JsonResponse

from django.db.models import Q, Avg, Sum, Max, Min, Count
from properties.models import Property
from django.http import JsonResponse

def is_beachfront(property):
    keywords = ['beachfront', 'seafront', 'oceanfront']
    return any(keyword in property.general_features.lower() for keyword in keywords) or \
           any(keyword in property.location_description.lower() for keyword in keywords)

# Then use this function in your filter:
# if persona == 'house_villa':
#     beachfront_filter = Q(pk__in=[p.pk for p in Property.objects.all() if is_beachfront(p)])
#     filters &= beachfront_filter


def get_properties_by_persona(request):
    persona = request.GET.get('persona')
    filters = Q(sold=False) & Q(accessible_to_foreigners=True)  # Exclude sold properties

    if persona == 'house_villa':
        filters &= Q(type='House / Villa') & \
                   Q(land_surface__gte=0, land_surface__lte=5000) & \
                   Q(interior_surface__gte=350, interior_surface__lte=400)
    elif persona == 'apartment':
        filters &= Q(type='Apartment') & \
                   Q(interior_surface__gte=0, interior_surface__lte=250)
    elif persona == 'penthouse':
        filters &= Q(type='Penthouse') & \
                   Q(interior_surface__gte=300) & \
                   (Q(general_features__icontains='beachfront') | Q(location_description__icontains='beachfront'))

    properties = Property.objects.filter(filters)
    agency_data = properties.values('agency').annotate(
        total_value=Sum('price'),
        average_value=Avg('price'),
        max_value=Max('price'),
        min_value=Min('price'),
        count=Count('id')
    ).order_by('-average_value')[:5]  # Get top 5

    return JsonResponse(list(agency_data), safe=False)


# views.py
from django.http import JsonResponse
from .models import Property
from django.db.models import Count

from django.db.models import Q, Avg
from django.http import JsonResponse
from properties.models import Property

def get_average_price_per_sq_meter(request):
    property_type = request.GET.get('property_type')
    region = request.GET.get('region')

    filter_conditions = Q(sold=False)  # Exclude sold properties
    if property_type and property_type != 'All':
        filter_conditions &= Q(type__icontains=property_type)
    if region and region != 'All':
        filter_conditions &= Q(location__icontains=region)

    avg_price_per_sq_meter = Property.objects.filter(filter_conditions).aggregate(
        average_price_per_sq_meter=Avg('price') / Avg('interior_surface')
    )['average_price_per_sq_meter']

    return JsonResponse({'average_price_per_sq_meter': avg_price_per_sq_meter}, safe=False)


from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from properties.models import Property

def get_agency_details(request):
    agency_id = request.GET.get('agencyId')
    property_type = request.GET.get('property_type')
    region = request.GET.get('region')

    if not agency_id:
        return JsonResponse({'error': 'Missing agency identifier'}, status=400)

    # Apply filters for property type and region if provided
    filters = Q(agency=agency_id) & Q(sold=False)  # Exclude sold properties
    if property_type and property_type != 'All':
        filters &= Q(type=property_type)
    if region and region != 'All':
        filters &= Q(location__icontains=region)

    # Fetch properties for the specified agency with filters
    properties = Property.objects.filter(filters)
    property_type_distribution = properties.values('type').annotate(count=Count('id')).order_by('-count')

    # Calculate the average price per square meter for the agency
    avg_price_per_sq_meter = properties.aggregate(avg_price=Avg('price') / Avg('interior_surface'))['avg_price']
    
    data = {
        'property_type_distribution': list(property_type_distribution),
        'average_price_per_sq_meter': avg_price_per_sq_meter if avg_price_per_sq_meter else 0  # Handle potential None value
    }

    return JsonResponse(data, safe=False)

from datetime import datetime
from django.db.models import OuterRef, Subquery, F, FloatField, ExpressionWrapper, Max
from django.db.models.functions import Abs
from django.http import JsonResponse
from .models import Property, PropertyPriceHistory
from django.utils import timezone
from datetime import datetime, timedelta


class Abs(Func):
    function = 'ABS'

def get_price_changes(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    property_type = request.GET.get('property_type')
    region = request.GET.get('region')
    sort_by = request.GET.get('sort_by', 'price_change')  # Default sort by price change

    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Fetch price changes within the date range
    price_changes = PropertyPriceHistory.objects.filter(
        property__sold=False  # Exclude sold properties
    ).select_related('property')

    # Apply filters for property type and region
    if property_type and property_type != 'All':
        price_changes = price_changes.filter(property__type=property_type)
    if region and region != 'All':
        price_changes = price_changes.filter(property__region__name=region)

    # Find previous price history entry for each price change
    previous_price_subquery = PropertyPriceHistory.objects.filter(
        property_id=OuterRef('property_id'),
        date__lt=OuterRef('date')
    ).order_by('-date').values('price')[:1]

    # Annotate the query with previous price, price change, and percentage change
    price_changes = price_changes.annotate(
        previous_price=Subquery(previous_price_subquery),
        price_change=ExpressionWrapper(F('price') - F('previous_price'), output_field=FloatField()),
        price_change_absolute=ExpressionWrapper(Abs(F('price') - F('previous_price')), output_field=FloatField()),
        price_change_percentage=ExpressionWrapper((F('price') - F('previous_price')) / F('previous_price') * 100, output_field=FloatField()),
        price_change_date=F('date')  # Get the date of the price change
    ).exclude(price_change=0)

    # Sorting
    if sort_by == 'price_change':
        price_changes = price_changes.order_by('-price_change_absolute')
    elif sort_by == 'interior_size':
        price_changes = price_changes.order_by('-property__interior_surface')

    # Calculate the date one week ago
    one_week_ago = datetime.now() - timedelta(days=7)

    # Filter latest properties
    latest_properties = Property.objects.filter(
        Q(sold=False),  # Exclude sold properties
        date_added__gte=one_week_ago,
        **({'type': property_type} if property_type != 'All' else {}),
        **({'location__icontains': region} if region != 'All' else {})  # Use icontains for partial match
    ).order_by('-date_added')

    # Prepare latest properties data
    latest_properties_data = [
        {
            'id': prop.id,
            'title': prop.title,
            'price': prop.price,
            'date_added': prop.date_added,
            'details_link': prop.details_link,
        }
        for prop in latest_properties
    ]

    # Prepare price changes data
    data = {
        'price_changes': [{
            'property_id': change.property.id,
            'property_title': change.property.title,
            'current_price': change.price,
            'previous_price': change.previous_price,
            'price_change': change.price_change,
            'price_change_percentage': change.price_change_percentage,
            'price_up': change.price > change.previous_price if change.previous_price is not None else None,
            'details_link': change.property.details_link,
            'price_change_date': change.price_change_date  # Correctly reference the date of the price change
        } for change in price_changes],
        'latest_properties': latest_properties_data
    }

    # Return response as JSON
    return JsonResponse(data, safe=False)

def get_latest_properties(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    property_type = request.GET.get('property_type')
    region = request.GET.get('region')
    sort_by = request.GET.get('sort_by', 'date_added')  # Default to sorting by date_added

    # Convert string dates to datetime objects
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Calculate the date one week ago
    one_week_ago = datetime.now() - timedelta(days=7)

    # Build the filter conditions
    filter_conditions = Q(sold=False, date_added__gte=one_week_ago)
    if property_type and property_type != 'All':
        filter_conditions &= Q(type=property_type)
    if region and region != 'All':
        filter_conditions &= Q(location__icontains=f', {region}')

    # Filter latest properties
    latest_properties = Property.objects.filter(filter_conditions).order_by(sort_by)

    # Prepare latest properties data
    latest_properties_data = [
        {
            'id': prop.id,
            'title': prop.title,
            'price': prop.price,
            'date_added': prop.date_added,
            'details_link': prop.details_link,
            'interior_surface': prop.interior_surface,  # Include interior surface
            'location': prop.location,  # Include location
        }
        for prop in latest_properties
    ]

    # Return response as JSON
    return JsonResponse({'latest_properties': latest_properties_data}, safe=False)

from django.http import JsonResponse
from .models import PropertyPriceHistory

def get_price_history(request, property_id):
    price_history = PropertyPriceHistory.objects.filter(property_id=property_id, property__sold=False).order_by('date')

    data = [{
        'date': entry.date,
        'price': entry.price
    } for entry in price_history]

    return JsonResponse(data, safe=False)

from django.http import JsonResponse
from .models import PropertyPriceHistory

from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import PropertyPriceHistory

def get_historical_prices(request):
    property_type = request.GET.get('property_type', 'All')
    region = request.GET.get('region', 'All')
    
    queryset = PropertyPriceHistory.objects.filter(property__sold=False)
    if property_type != 'All':
        queryset = queryset.filter(property__type=property_type)
    if region != 'All':
        queryset = queryset.filter(property__region__name=region)
    
    paginator = Paginator(queryset.values('date', 'price'), 50)  # Show 50 prices per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return JsonResponse(list(page_obj.object_list), safe=False)

    return JsonResponse(list(page_obj.object_list), safe=False)
from django.db.models import Avg
from django.http import JsonResponse
from .models import PropertyPriceHistory

def get_average_prices(request):
    property_type = request.GET.get('property_type', 'All')
    region = request.GET.get('region', 'All')
    
    queryset = PropertyPriceHistory.objects.filter(property__sold=False)
    if property_type != 'All':
        queryset = queryset.filter(property__type=property_type)
    if region != 'All':
        queryset = queryset.filter(property__region__name=region)
    
    # Group by month and calculate the average price
    average_prices = queryset.extra(select={'month': "DATE_TRUNC('month', date)"}).values('month').annotate(avg_price=Avg('price')).order_by('month')

    return JsonResponse(list(average_prices), safe=False)

from django.db.models import Avg
from django.http import JsonResponse
from .models import PropertyPriceHistory

from django.db.models import Avg
from django.http import JsonResponse
from .models import PropertyPriceHistory
from django.db.models import Avg
from django.http import JsonResponse
from .models import PropertyPriceHistory
from django.db.models.functions import TruncDay

def get_rolling_average_prices(request):
    property_type = request.GET.get('property_type', 'All')
    region = request.GET.get('region', 'All')
    location = request.GET.get('location', '')
    print(location)

    queryset = PropertyPriceHistory.objects.filter(property__sold=False)
    if property_type != 'All':
        queryset = queryset.filter(property__type=property_type)
    if region != 'All':
        queryset = queryset.filter(property__region__name=region)
    if location:
        queryset = queryset.filter(property__location__icontains=location)
    
    # Aggregate average prices by date
    date_prices = queryset.annotate(
        truncated_date=TruncDay('date')
    ).values('truncated_date').annotate(
        avg_price=Avg('price')
    ).order_by('truncated_date')

    return JsonResponse(list(date_prices), safe=False)


from django.http import JsonResponse
from .models import Property

from django.http import JsonResponse
from .models import Property

def get_sold_properties(request):
    property_type = request.GET.get('property_type', 'All')
    region = request.GET.get('region', 'All')

    properties = Property.objects.filter(sold=True)

    if property_type != 'All':
        properties = properties.filter(type=property_type)
    
    if region != 'All':
        properties = properties.filter(region__name=region)
    
    data = [{
        'id': prop.id,
        'title': prop.title,
        'price': prop.price,
        'date_added': prop.date_added,
        'details_link': prop.details_link,
        'location': prop.location,
        'description': prop.description,
        'agency_name': prop.agency_name,
        'land_surface': prop.land_surface,
        'interior_surface': prop.interior_surface,
        'swimming_pool': prop.swimming_pool,
        'construction_year': prop.construction_year,
        'bedrooms': prop.bedrooms,
        'bathrooms': prop.bathrooms,
        'toilets': prop.toilets,
        'aircon': prop.aircon,
        'general_features': prop.general_features,
        'indoor_features': prop.indoor_features,
        'outdoor_features': prop.outdoor_features,
        'location_description': prop.location_description,
        'type': prop.type,
        'ref': prop.ref,
    } for prop in properties]

    return JsonResponse(data, safe=False)



from django.http import JsonResponse
from .models import Property
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_http_methods(["POST"])
def update_sold_status(request):
    data = json.loads(request.body)
    property_id = data.get('property_id')
    sold_status = data.get('sold')

    try:
        property = Property.objects.get(id=property_id)
        property.sold = sold_status
        property.save()
        return JsonResponse({'status': 'success'})
    except Property.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Property not found'}, status=404)


# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from properties.models import Location

class LocationListView(APIView):
    def get(self, request):
        region = request.GET.get('region', None)
        property_type = request.GET.get('property_type', None)
        
        if region and region != 'All':
            locations = Location.objects.filter(region=region)
        else:
            locations = Location.objects.all()
        
        if property_type and property_type != 'All':
            location_ids = Property.objects.filter(type=property_type).values_list('location', flat=True)
            locations = locations.filter(id__in=location_ids)
        
        data = [{'id': loc.id, 'name': loc.name, 'region': loc.region} for loc in locations]
        return Response(data)