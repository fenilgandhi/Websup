from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^index$', views.index, name='index'),
    url(r'^bulk_whatsapp$', views.bulk_whatsapp, name='bulk_whatsapp'),
]