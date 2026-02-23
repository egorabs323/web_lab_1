from django.urls import path
from . import views, converters
from django.urls import register_converter

register_converter(converters.VINConverter, 'vin')

urlpatterns = [
    path('', views.index, name='home'),
    path('cars/', views.cars, name='cars'),
    path('cars/<slug:brand_slug>/', views.brand, name='brand'),
    path('cars/<slug:brand_slug>/<slug:model_slug>/', views.model, name='model'),
    path('vin/<vin:vin_code>/', views.vin_info, name='vin_info'),
]