"""
Custom template tags and filters for the accounts app.
"""
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def currency(value):
    """
    Format a number as currency with the configured currency symbol.
    Usage: {{ amount|currency }}
    Example: {{ 100.50|currency }} -> ₵ 100.50
    """
    try:
        value = float(value)
        return f"{settings.CURRENCY_SYMBOL} {value:,.2f}"
    except (ValueError, TypeError):
        return value


@register.simple_tag
def currency_symbol():
    """
    Return the currency symbol.
    Usage: {% currency_symbol %}
    """
    return settings.CURRENCY_SYMBOL


@register.simple_tag
def currency_code():
    """
    Return the currency code.
    Usage: {% currency_code %}
    """
    return settings.CURRENCY_CODE
