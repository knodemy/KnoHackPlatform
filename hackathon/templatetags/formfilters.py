from django import template
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.auth.models import User

register = template.Library()

@register.filter(name='addcss')
def addcss(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter(name='addplaceholder')
def addplaceholder(value, arg):
    return value.as_widget(attrs={'placeholder': arg})

@register.filter(name='formattr')
def attr(obj, arg1):
    att, value = arg1.split("=")
    obj.field.widget.attrs[att] = value
    return obj
