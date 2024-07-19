from rest_framework import serializers
from .models import Property, PricePerSquareMeter, Region

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class PricePerSquareMeterSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = PricePerSquareMeter
        fields = '__all__'
from rest_framework import serializers
from properties.models import Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'region', 'latitude', 'longitude']
