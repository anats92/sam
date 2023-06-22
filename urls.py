from django.urls import path

from .views import health_check, total_cost, reset_cost, quote_data, quote_data_with_rate_limits

urlpatterns = [
    path('health_check/', health_check, name='health_check'),
    path('quote-data/<str:symbol>/', quote_data, name='quote_data'),
    path('quote-data-rate-limits/<str:symbol>/', quote_data_with_rate_limits, name='quote_data_rate_limits'),
    path('total-cost/', total_cost, name='total_cost'),
    path('reset-cost-counter/', reset_cost, name='reset_cost_counter'),
]
