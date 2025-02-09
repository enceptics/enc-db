from django.urls import path
from weather.views import get_weather

urlpatterns = [
    path('weather-forecast/<str:place_name>/', get_weather, name='get_weather'),
]
