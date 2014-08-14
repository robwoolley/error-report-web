from datetime import datetime, timedelta
import re
from django import template
from django.utils import timezone
from django.template.defaultfilters import filesizeformat

register = template.Library()

@register.filter(name = 'sortcols')
def sortcols(tablecols):
    return sorted(tablecols, key = lambda t: t['name'])

