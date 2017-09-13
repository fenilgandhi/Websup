from django.contrib import admin
from Clientapp.models import *

# Register your models here.
admin.site.register(MyUser)
admin.site.register(Plan)
admin.site.register(User_Plan)
admin.site.register(WhatsApp_Individual_Message)
admin.site.register(WhatApp_Message_Format)
admin.site.register(Contact)