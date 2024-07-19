from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from properties.views import PropertyViewSet, PricePerSquareMeterViewSet, RegionViewSet, CurrentMarketValueView

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'prices', PricePerSquareMeterViewSet)
router.register(r'regions', RegionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/current_market_value/', CurrentMarketValueView.as_view(), name='current-market-value'),
]
