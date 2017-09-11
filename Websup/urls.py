##	Websup URL Configuration

from django.conf.urls import url
from django.contrib import admin
import Clientapp.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^aboutus$', Clientapp.views.aboutus, name='clientapp_aboutus'),
    url(r'^plans$', Clientapp.views.plans, name='clientapp_plans'),
    url(r'^contactus$', Clientapp.views.contactus, name='clientapp_contactus'),


    ## Clientapp
    url('^$' , Clientapp.views.dashboard , name="clientapp_dashboard"),
    url('^send$', Clientapp.views.send,  name="clientapp_send"),
    url('^report$', Clientapp.views.report,  name="clientapp_report"),

    ## Login 


    ## Api 


    ## Whatsapp

]
