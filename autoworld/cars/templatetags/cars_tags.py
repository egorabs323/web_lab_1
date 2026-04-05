from django import template
from django.db.models import Count
from cars.models import Car, CarCategory, CarTag

register = template.Library()


@register.simple_tag
def get_brands():
    brands = Car.objects.filter(is_published=1).values_list('brand', flat=True).distinct().order_by('brand')
    return [{'name': b.lower().replace(' ', '-'), 'display': b} for b in brands]


@register.inclusion_tag('cars/list_categories.html')
def show_categories(cat_selected_id=0):
    cats = CarCategory.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0)
    return {"cats": cats, "cat_selected": cat_selected_id}


@register.inclusion_tag('cars/list_tags.html')
def show_all_tags():
    tags = CarTag.objects.annotate(cars_count=Count('cars')).filter(cars_count__gt=0)
    return {"tags": tags}