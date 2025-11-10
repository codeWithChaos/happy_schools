from django import template

register = template.Library()

@register.filter
def index(dictionary, key):
    """Access dictionary value by key."""
    if dictionary and key:
        return dictionary.get(key)
    return None
