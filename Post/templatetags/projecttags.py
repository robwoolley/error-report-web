from datetime import datetime, timedelta
import re
from django import template
from django.utils import timezone
from django.template.defaultfilters import filesizeformat

register = template.Library()

@register.filter(name = 'sortcols')
def sortcols(tablecols):
    return sorted(tablecols, key = lambda t: t['name'])

@register.filter(name = 'can_be_filter')
def can_be_filter(args, details):
    arg_list = [arg.strip() for arg in args.split(':')]
    if arg_list[1] == "RECIPE":
        aux = len(filter(lambda x: x.RECIPE == arg_list[0], details))
    elif arg_list[1] == "TASK":
        aux = len(filter(lambda x: x.TASK == arg_list[0], details))
    elif arg_list[1] == "MACHINE":
        aux = len(filter(lambda x: x.BUILD.MACHINE == arg_list[0], details))
    elif arg_list[1] == "DISTRO":
        aux = len(filter(lambda x: x.BUILD.DISTRO == arg_list[0], details))
    elif arg_list[1] == "BUILD_SYS":
        aux = len(filter(lambda x: x.BUILD.BUILD_SYS == arg_list[0], details))
    elif arg_list[1] == "TARGET_SYS":
        aux = len(filter(lambda x: x.BUILD.TARGET_SYS == arg_list[0], details))
    elif arg_list[1] == "NATIVELSBSTRING":
        aux = len(filter(lambda x: x.BUILD.NATIVELSBSTRING == arg_list[0], details))
    elif arg_list[1] == "BRANCH":
        aux = len(filter(lambda x: x.BUILD.BRANCH == arg_list[0], details))
    elif arg_list[1] == "NAME":
        aux = len(filter(lambda x: x.BUILD.NAME == arg_list[0], details))
    elif arg_list[1] == "COMMIT":
        aux = len(filter(lambda x: x.BUILD.COMMIT == arg_list[0], details))

    return  aux > 1 and aux < len(details)

@register.filter(name='getFilterValue')
def getFilterValue(value, arg):
    return value.split(arg)[0]
