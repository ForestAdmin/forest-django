from django.conf.urls import url
from forest import views
# from forest.views import Resources

urlpatterns = [
    url(r'^forest$', views.empty),
    url(r'^forest/sessions$', views.session),
    url(r'(?i)^forest/(?P<model>[a-z]*)$', views.resources),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)$', views.resource),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/(?P<association>[a-z]*)$', views.association),
]
