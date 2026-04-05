from django.contrib import admin
from .models import Car, CarCategory, CarTag, CarEngine

@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('id', 'name', 'slug')

@admin.register(CarTag)
class CarTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("tag",)}
    list_display = ('id', 'tag', 'slug')

@admin.register(CarEngine)
class CarEngineAdmin(admin.ModelAdmin):
    list_display = ('id', 'engine_type', 'displacement', 'horsepower')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("brand", "model_name")}
    # Временно убраны category и tags, чтобы не падала проверка
    list_filter = ('is_published', 'year', 'body_type')
    search_fields = ('brand', 'model_name', 'vin')
    list_display = ('id', 'brand', 'model_name', 'year', 'price', 'is_published')