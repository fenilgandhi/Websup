from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'whatsapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	# url(r'^register/$', views.register, name='signup'),
 #    url(r'^activate/(?P<pk>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
 #        views.activate_new_user, name='activate_user'),
    # url(r'^login/$', views.login,
    #     {'template_name': 'login.html', 'authentication_form': LoginForm, },
    #     name='login'),
    # url(r'^logout/$', a_views.logout, {'next_page': '/login'}),	
	url(r'', include('dashboard.urls')),
    url(r'^admin/', include(admin.site.urls)),

]

