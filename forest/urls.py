from django.conf.urls import url
from forest import views
# from forest.views import Resources

urlpatterns = [
    url(r'^forest$', views.empty),
    url(r'^forest/sessions$', views.session),
    url(r'(?i)^forest/(?P<model>[a-z]*)$', views.resources),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)$', views.resource),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/(?P<association>[a-z]*)$', views.association),
    url(r'(?i)^forest/stats/(?P<model>[a-z]*)$', views.stats),
    url(r'(?i)^forest/stripe_payments$', views.stripe_payments),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/stripe_payments$', views.stripe_payments),
    url(r'(?i)^forest/stripe_payments/refunds$', views.stripe_refund),
    url(r'(?i)^forest/stripe_invoices$', views.stripe_refund),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/stripe_invoices$', views.stripe_invoices),
    url(r'(?i)^forest/(?P<model>[a-z]*)/(?P<r_id>[0-9]+)/stripe_cards$', views.stripe_cards),
]
