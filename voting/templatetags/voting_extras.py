from django import template
from itertools import groupby
from operator import attrgetter

register = template.Library()

@register.filter
def groupby_attr(objects, attribute):
    """
    Groups objects by a specified attribute
    
    Usage: {% for group_name, group_items in objects|groupby_attr:"attribute_name" %}
    """
    if objects:
        return [(group_name, list(items)) for group_name, items in groupby(objects, attrgetter(attribute))]
    return []


@register.filter
def get_field(form, field_name):
    """
    Access a form field by name dynamically.
    
    Usage: {{ form|get_field:"field_name" }}
    """
    try:
        return form[field_name]
    except KeyError:
        return None
