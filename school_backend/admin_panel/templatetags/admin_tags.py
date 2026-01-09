# admin_panel/templatetags/admin_tags.py
from django import template

register = template.Library()

@register.simple_tag
def get_admin_settings():
    '''Get admin settings'''
    return {}

@register.filter
def format_date(value):
    '''Format date for admin display'''
    if value:
        return value.strftime('%Y-%m-%d %H:%M')
    return ''