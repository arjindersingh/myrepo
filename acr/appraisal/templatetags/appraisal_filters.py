from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# --- Filters ---

@register.filter
def get_item(dictionary, key):
    """Safe dictionary lookup for templates"""
    try:
        return dictionary.get(key)
    except Exception:
        return None

@register.filter
def field_by_name(form, name):
    try:
        return form[name]
    except KeyError:
        return mark_safe('<span class="text-danger">Missing field: {}</span>'.format(name))

@register.filter
def concat(a, b):
    """String concatenation: 'item_'|concat:item.id"""
    return f"{a}{b}"

# --- Simple tags ---

@register.simple_tag
def cell_get(cell_dict, emp_id, type_id):
    return cell_dict.get((emp_id, type_id))

@register.simple_tag
def dict_get(d, key):
    return d.get(key)
