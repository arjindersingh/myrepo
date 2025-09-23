from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, False)

@register.filter
def widget_type(field):
    return field.field.widget.__class__.__name__.lower()
