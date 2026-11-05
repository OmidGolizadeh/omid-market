from django import template
from django.utils.safestring import mark_safe
import jdatetime

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


@register.filter()
def jalali_date(value, with_time=True):
    if not value:
        return ''

    if isinstance(value, jdatetime.datetime):
        date = value
    else:
        date = jdatetime.datetime.fromgregorian(datetime=value)

    months = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
    ]

    result = f'{date.day} {months[date.month - 1]} {date.year}'
    if with_time:
        result += f'، ساعت {date.hour:02d}:{date.minute:02d}'

    return result.translate(
        str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    )

@register.filter()
def group4_fa(value):
    if value is None:
        return ''
    s = ''.join(ch for ch in str(value) if ch.isdigit())
    result = ' '.join(s[i:i + 4] for i in range(0, len(s), 4))
    return result.translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))