from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.defaults import page_not_found

from Clientapp.admin import admin_view
admin.site.admin_view = admin_view
import Clientapp.views

##  Websup URL Configuration
urlpatterns = [
    # url(r'^admin/login', page_not_found),
    url(r'^admin/', admin.site.urls),

    ## Clientapp
    url(r'^$' , login_required(Clientapp.views.dashboard) , name="clientapp_dashboard"),
    url(r'^send$', login_required(Clientapp.views.send) ,  name="clientapp_send"),
    url(r'^report$', login_required(Clientapp.views.report),  name="clientapp_report"),

    ## Login 
    url(r'^user/login/$', auth_views.login, {'template_name' : 'registration/login.html'}, name='auth_login'),
    url(r'^user/logout/$', login_required(auth_views.logout), {'template_name' : 'registration/logout.html'}, name='auth_logout'),
    url(r'^user/changepassword/$', login_required(auth_views.password_change), {'post_change_redirect': 'password_change_done'}, name='password_change'),
    url(r'^user/passwordchanged/$', login_required(auth_views.password_change_done), name='password_change_done'),

    ## Api 
    url(r'^admin/whatsapp$', staff_member_required(Clientapp.views.api_gui), name='whatsapp_gui'),
    url(r'^api/(?P<command>[a-z]+)/$' , staff_member_required(Clientapp.views.api), name="whatsapp_api"),
]


if settings.DEBUG is True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
