from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from properties.views import AgencyRankingView, ExchangeRatesView, InvestmentOpportunitiesView, LocationHeatmapView, LocationListView, MetricsView, PriceDistributionView, PricePerSquareMeterView, PriceVsAccessibleView, PropertyTypeDistributionView, PropertyViewSet, PricePerSquareMeterViewSet, RegionViewSet, CurrentMarketValueView, ScatterPlotDataView, get_agency_details, get_average_price_per_sq_meter, get_average_prices, get_historical_prices, get_latest_properties,  get_price_changes, get_price_history, get_properties_by_persona, get_rolling_average_prices, get_sold_properties, update_sold_status
from valuation_tool.views import DistinctFeaturesView, ValuationPredictionView
router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'prices', PricePerSquareMeterViewSet)
router.register(r'regions', RegionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/current_market_value/', CurrentMarketValueView.as_view(), name='current-market-value'),
    path('api/price_per_square_meter/', PricePerSquareMeterView.as_view(), name='price-per-square-meter'),
    path('api/price_distribution/', PriceDistributionView.as_view(), name='price-distribution'),
    # path('api/locations/', LocationHeatmapView.as_view(), name='location-heatmap'),
    path('api/exchange_rates/', ExchangeRatesView.as_view(), name='exchange_rates'),
    path('api/metrics/',MetricsView.as_view(), name='metrics'),
    path('api/agency-ranking/', AgencyRankingView.as_view(), name='agency-ranking'),
    path('api/predict/', ValuationPredictionView.as_view(), name='valuation_prediction'),
    path('api/distinct_features/', DistinctFeaturesView.as_view(), name='distinct_features'),
    path('api/investment-opportunities/', InvestmentOpportunitiesView.as_view(), name='investment-opportunities'),
    path('api/property_type_distribution/', PropertyTypeDistributionView.as_view(), name='property_type_distribution'),
    path('api/scatter_plot_data/', ScatterPlotDataView.as_view(), name='scatter-plot-data'),
    path('api/price_vs_accessible/', PriceVsAccessibleView.as_view(), name='price_vs_accessible'),
    path('api/properties_by_persona/', get_properties_by_persona, name='properties_by_persona'),
    path('api/agency-details/', get_agency_details, name='agency-details'),
    path('api/average-price-per-sq-meter/', get_average_price_per_sq_meter, name='average-price-per-sq-meter'),
    path('api/price-changes/', get_price_changes, name='price-changes'),
    path('api/price-history/<int:property_id>/', get_price_history, name='price-history'),
    path('api/historical-prices/', get_historical_prices, name='historical-prices' ), 
    path('api/average-prices/', get_average_prices, name='average-prices'),
    path('api/rolling-average-prices/', get_rolling_average_prices, name='rolling-average-prices'),
    path('api/sold-properties/', get_sold_properties, name='get_sold_properties'),
    path('api/update-sold-status/', update_sold_status, name='update_sold_status'),
    path('api/latest-properties/', get_latest_properties, name='latest-properties'),
    path('api/locations/', LocationListView.as_view(), name='location-heatmap'),



]
