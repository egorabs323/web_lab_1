from django.urls import path
from . import views

app_name = 'cars'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:cat_slug>/', views.show_category, name='category'),
    path('tag/<slug:tag_slug>/', views.show_tag, name='tag'),
    path('categories/', views.categories_list, name='categories_list'),
    path('tags/', views.tags_list, name='tags_list'),
    path('cars/', views.cars_list, name='cars_list'),
    path('brands/', views.brands_list, name='brands_list'),
    path('cars/<slug:brand_slug>/', views.brand, name='brand'),
    path('car/<slug:car_slug>/', views.car_detail, name='car_detail'),
    path('vin/<str:vin_code>/', views.vin_info, name='vin_check'),
    path('add-car/', views.add_car, name='add_car'),
    path('add-car-model/', views.add_car_model, name='add_car_model'),
    path('upload/', views.upload_file, name='upload_file'),
]