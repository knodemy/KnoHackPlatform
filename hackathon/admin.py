from django.contrib import admin
from hackathon.models import *
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from hackathon.forms import *
from django.utils.translation import ugettext_lazy as _


admin.site.register(Event)
admin.site.register(EventRegister)
admin.site.register(ProgramFlow)
admin.site.register(Teams)
admin.site.register(UserProfile)