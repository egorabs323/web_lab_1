from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Админ-панель автомобилей"
admin.site.index_title = "Управление автосалоном"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('', include('cars.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)