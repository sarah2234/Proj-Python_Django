from django import template

register = template.Library()





@register.filter
def key(value):
    return list(value.keys())[0]


@register.filter
def date(value):
    if value == 0:
        return '월'
    if value == 1:
        return '화'
    if value == 2:
        return '수'
    if value == 3:
        return '목'
    if value == 4:
        return '금'
    if value == 5:
        return '토'
    if value == 6:
        return '일'

