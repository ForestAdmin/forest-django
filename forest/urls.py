from django.conf.urls import url
from forest import views
from forest.views import empty, session, resources, resource, association, stat

urlpatterns = [
    url(r'^forest$', empty),
    url(r'^forest/sessions$', session),
    url(r'(?i)^forest/(?P<model>[a-z]*)$', resources),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)$', resource),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/(?P<association>[a-z]*)$', association),
    url(r'(?i)^forest/stats/(?P<model>[a-z]*)$', stat),
    # url(r'(?i)^forest/stripe_payments$', views.stripe_payments),
    # url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/stripe_payments$', views.stripe_payments),
    # url(r'(?i)^forest/stripe_payments/refunds$', views.stripe_refund),
    # url(r'(?i)^forest/stripe_invoices$', views.stripe_refund),
    # url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/stripe_invoices$', views.stripe_invoices),
    # url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/stripe_cards$', views.stripe_cards),
]
