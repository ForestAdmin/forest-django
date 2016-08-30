import json
import requests
import os

from django.conf import settings
from django.apps import AppConfig
from forest.generators.schemas import api_map
from forest.services.utils import get_model_class

def setup_stripe_integration(apimap):
    model = get_model_class(settings.FOREST_STRIPE_USER_COLLECTION)
    reference_name = model.__name__
    apimap.append({
        'name': 'stripe_payments',
        'isVirtual': True,
        'isReadOnly': True,
        'fields': [
          { 'field': 'id', 'type': 'String', 'isSearchable': False },
          { 'field': 'created', 'type': 'Date', 'isSearchable': False },
          { 'field': 'amount', 'type': 'Number', 'isSearchable': False },
          { 'field': 'status', 'type': 'String', 'isSearchable': False },
          { 'field': 'currency', 'type': 'String', 'isSearchable': False },
          { 'field': 'refunded', 'type': 'Boolean', 'isSearchable': False },
          { 'field': 'description', 'type': 'String', 'isSearchable': False },
          {
            'field': 'customer',
            'type': 'String',
            'reference': reference_name,
            'isSearchable': False
          }
        ],
        'actions': [{
          'name': 'Refund',
          'endpoint': '/forest/stripe_payments/refunds'
        }]
    })

    apimap.append({
        'name': 'stripe_invoices',
        'isVirtual': True,
        'isReadOnly': True,
        'fields': [
          { 'field': 'id', 'type': 'String', 'isSearchable': False },
          { 'field': 'amount_due', 'type': 'Number', 'isSearchable': False },
          { 'field': 'attempt_count', 'type': 'Number', 'isSearchable': False },
          { 'field': 'attempted', 'type': 'Boolean', 'isSearchable': False },
          { 'field': 'closed', 'type': 'Boolean', 'isSearchable': False },
          { 'field': 'currency', 'type': 'String', 'isSearchable': False },
          { 'field': 'date', 'type': 'Date', 'isSearchable': False },
          { 'field': 'forgiven', 'type': 'Boolean', 'isSearchable': False },
          { 'field': 'period_start', 'type': 'Date', 'isSearchable': False },
          { 'field': 'period_end', 'type': 'Date', 'isSearchable': False },
          { 'field': 'subtotal', 'type': 'Number', 'isSearchable': False },
          { 'field': 'total', 'type': 'Number', 'isSearchable': False },
          { 'field': 'application_fee', 'type': 'Number', 'isSearchable': False },
          { 'field': 'tax', 'type': 'Number', 'isSearchable': False },
          { 'field': 'tax_percent', 'type': 'Number', 'isSearchable': False },
          {
            'field': 'customer',
            'type': 'String',
            'reference': reference_name,
            'isSearchable': False
          }
        ]
    })

    apimap.append({
        'name': 'stripe_cards',
        'isVirtual': True,
        'isReadOnly': True,
        'onlyForRelationships': True,
        'fields': [
            { 'field': 'id', 'type': 'String', 'isSearchable': False },
            { 'field': 'last4', 'type': 'String', 'isSearchable': False },
            { 'field': 'brand', 'type': 'String', 'isSearchable': False },
            { 'field': 'funding', 'type': 'String', 'isSearchable': False },
            { 'field': 'exp_month', 'type': 'Number', 'isSearchable': False },
            { 'field': 'exp_year', 'type': 'Number', 'isSearchable': False },
            { 'field': 'country', 'type': 'String', 'isSearchable': False },
            { 'field': 'name', 'type': 'String', 'isSearchable': False },
            { 'field': 'address_line1', 'type': 'String', 'isSearchable': False },
            { 'field': 'address_line2', 'type': 'String', 'isSearchable': False },
            { 'field': 'address_city', 'type': 'String', 'isSearchable': False },
            { 'field': 'address_state', 'type': 'String', 'isSearchable': False },
            { 'field': 'address_zip', 'type': 'String', 'isSearchable': False },
            { 'field': 'address_country', 'type': 'String', 'isSearchable': False },
            { 'field': 'cvc_check', 'type': 'String', 'isSearchable': False },
            {
                'field': 'customer',
                'type': 'String',
                'reference': reference_name,
                'isSearchable': False
            }
        ]
    })


class ForestConfig(AppConfig):
    name = 'forest'
    verbose_name = "My Forest Connector"
    def ready(self):
        apimap = api_map.generate()
        # setup_stripe_integration(apimap['data'])
        url = os.getenv('FOREST_URL', settings.FOREST_URL)
        url += '/forest/apimaps'
        secret_key = os.getenv('FOREST_SECRET_KEY', settings.FOREST_SECRET_KEY)
        headers = {
            'forest-secret-key':  secret_key,
            'Content-Type': 'application/json'
        }
        req = requests.post(url, data=json.dumps(apimap), headers=headers)
