from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.index, name='index'),
    path('cars/', views.cars_list, name='cars_list'),
    path('cars/<slug:brand_slug>/', views.brand, name='brand'),
    path('cars/<slug:brand_slug>/<slug:model_slug>/', views.model, name='model'),
    path('vin/<str:vin_code>/', views.vin_info, name='vin_check'),
]