from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
from django.db import models

class Agency(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


from django.db import models

class Property(models.Model):
    PROPERTY_TYPES = [
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('Land', 'Land'),
        ('Commercial Land', 'Commercial Land'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    details_link = models.URLField()
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    agency_name = models.CharField(max_length=255)  # Rename the existing field
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)  # ForeignKey field
    agency_logo = models.URLField(null=True, blank=True)
    contact_phone = models.CharField(max_length=50, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_whatsapp = models.CharField(max_length=50, null=True, blank=True)
    land_surface = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True)
    interior_surface = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Use the cleaned field
    swimming_pool = models.CharField(max_length=100, null=True, blank=True)
    construction_year = models.CharField(max_length=4, null=True, blank=True)
    bedrooms = models.IntegerField(null=True, blank=True)
    accessible_to_foreigners = models.BooleanField(default=False)
    bathrooms = models.IntegerField(null=True, blank=True)
    toilets = models.IntegerField(null=True, blank=True)
    aircon = models.BooleanField(default=False)
    general_features = models.TextField(null=True, blank=True)
    indoor_features = models.TextField(null=True, blank=True)
    outdoor_features = models.TextField(null=True, blank=True)
    location_description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    ref = models.CharField(max_length=50)
    sold = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)  

    def location_name(self):
        return self.location.split(',')[0].strip() if ',' in self.location else self.location

    

    def __str__(self):
        return self.title

class PropertyPriceHistory(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.title} - {self.price} on {self.date}"

class PricePerSquareMeter(models.Model):
    PROPERTY_TYPES = [
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('Land', 'Land'),
        ('Commercial Land', 'Commercial Land'),
    ]
    
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    price_per_square_meter = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.property_type} in {self.region.name}: {self.price_per_square_meter}"


from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.region}"


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3)
    rate = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
