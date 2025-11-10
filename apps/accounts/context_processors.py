"""
Context processors for the accounts app.
Adds global context variables to all templates.
"""
from django.conf import settings


def currency_context(request):
    """
    Add currency settings to template context.
    Makes CURRENCY_SYMBOL and CURRENCY_CODE available in all templates.
    """
    return {
        'CURRENCY_SYMBOL': settings.CURRENCY_SYMBOL,
        'CURRENCY_CODE': settings.CURRENCY_CODE,
    }
