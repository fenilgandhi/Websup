from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
import Clientapp.views

##  Websup URL Configuration
urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^aboutus$', Clientapp.views.aboutus, name='aboutus'),
    url(r'^plans$', Clientapp.views.plans, name='plans'),
    url(r'^contactus$', Clientapp.views.contactus, name='contactus'),

    ## Clientapp
    url(r'^$' , Clientapp.views.dashboard , name="clientapp_dashboard"),
    url(r'^send$', Clientapp.views.send,  name="clientapp_send"),
    url(r'^report$', Clientapp.views.report,  name="clientapp_report"),

    ## Login 
    url(r'^user/login/$', auth_views.login, {'template_name' : 'registration/login.html'}, name='auth_login'),
    url(r'^user/logout/$', auth_views.logout, {'template_name' : 'registration/logout.html'}, name='auth_logout'),
    url(r'^user/changepassword/$', auth_views.password_change, {'post_change_redirect': 'password_change_done'}, name='password_change'),
    url(r'^user/passwordchanged/$', auth_views.password_change_done, name='password_change_done'),

    ## Api 
]
