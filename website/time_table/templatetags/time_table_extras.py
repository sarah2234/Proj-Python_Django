from django import template

register = template.Library()


@register.filter
def key(value):
    return list(value.keys())[0]