from django import template
from django.utils.safestring import mark_safe

register = template.Library()

persian_digits = str.maketrans(
    '0123456789',
    '۰۱۲۳۴۵۶۷۸۹'
)


@register.filter()
def toman(value):
    if value is None:
        return ""
    return f'{int(value):,}'.translate(persian_digits)


@register.filter()
def stars(score):
    score = float(score)

    full = int(score)
    half = (score - full) >= 0.5
    empty = 5 - full - (1 if half else 0)

    html = ''
    html += '<i class="fa fa-star"></i>' * full
    if half:
        html += '<i class="fa fa-star-half-alt"></i>'
    html += '<i class="far fa-star"></i>' * empty
    return mark_safe(html)
