from django import template
from .. import views

register = template.Library()

@register.simple_tag
def get_brands():
    return views.VALID_BRANDS