from django import template
from cars.models import Car

register = template.Library()


@register.simple_tag
def get_brands():
    brands = Car.objects.filter(is_published=1).values_list('brand', flat=True).distinct().order_by('brand')

    return [{'name': b.lower().replace(' ', '-'), 'display': b} for b in brands]