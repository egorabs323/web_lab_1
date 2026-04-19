from django.urls import path, include
from django.contrib import admin

admin.site.site_header = "Админ-панель автомобилей"
admin.site.index_title = "Управление автосалоном"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cars.urls')),
]