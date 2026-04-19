from django.contrib import admin, messages
from .models import Car, CarCategory, CarTag, CarEngine

@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)

@admin.register(CarTag)
class CarTagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("tag",)}
    list_display = ('id', 'tag', 'slug')
    search_fields = ('tag',)

@admin.register(CarEngine)
class CarEngineAdmin(admin.ModelAdmin):
    list_display = ('id', 'engine_type', 'displacement', 'horsepower')

class PriceFilter(admin.SimpleListFilter):
    title = 'Цена'
    parameter_name = 'price'

    def lookups(self, request, model_admin):
        return [
            ('cheap', 'До 1 млн'),
            ('medium', '1-3 млн'),
            ('expensive', 'Более 3 млн'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'cheap':
            return queryset.filter(price__lt=1000000)
        if self.value() == 'medium':
            return queryset.filter(price__gte=1000000, price__lte=3000000)
        if self.value() == 'expensive':
            return queryset.filter(price__gt=3000000)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):

    prepopulated_fields = {"slug": ("brand", "model_name")}

    list_display = (
        'brand', 'model_name', 'year',
        'price', 'is_published', 'category',
        'short_info', 'car_age'
    )

    list_display_links = ('brand', 'model_name')

    list_editable = ('is_published',)

    ordering = ['-time_create', 'price']

    list_per_page = 5

    search_fields = ('brand', 'model_name', 'vin', 'category__name')

    list_filter = ('is_published', 'year', 'body_type', 'category', PriceFilter)

    filter_horizontal = ['tags']

    @admin.display(description="Кратко")
    def short_info(self, obj):
        return f"{obj.brand} {obj.model_name} - {obj.price}$"

    @admin.display(description="Возраст авто")
    def car_age(self, obj):
        from datetime import datetime
        return datetime.now().year - obj.year

    @admin.action(description="Опубликовать выбранные")
    def make_published(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"Опубликовано: {count}")

    @admin.action(description="Снять с публикации")
    def make_unpublished(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"Снято: {count}", messages.WARNING)

    actions = ['make_published', 'make_unpublished']