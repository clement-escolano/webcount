from django import template
from django.utils.formats import number_format
from django.utils.translation import get_language

register = template.Library()

currencies = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "AUD": "A$",
    "CAD": "C$",
    "CHF": "CHF",
    "CNY": "¥",
    "INR": "₹",
    "BRL": "R$",
    "RUB": "₽",
}


@register.simple_tag
def format_money(amount: float, currency: str):
    language = get_language()
    number = number_format(round(amount, 2), force_grouping=True)
    symbol = currencies.get(currency, currency)
    if language == "en":
        return f"{symbol}{number}"
    return f"{number} {symbol}"
