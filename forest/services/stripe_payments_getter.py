import stripe
from django.conf import settings
from forest.services.utils import get_model_class


class StripePaymentsGetter():
    def __init__(self, params, model_name, r_id):
        self.model = get_model_class(model_name)
        self.r_id = r_id
        self.stripe = stripe
        self.stripe.api_key = settings.FOREST_STRIPE_API_KEY
        self.user_field = settings.FOREST_STRIPE_USER_FIELD
        self.params = params

    def _has_pagination(self):
        return self.params.get('page[number]')

    def _get_limit(self):
        if self._has_pagination():
            return int(self.params.get('page[size]', 10))
        else:
            return 10

    def _get_offset(self):
        if self._has_pagination():
            pages = int(self.params.get('page[number]'))
            return (pages - 1) * self._get_limit()
        else:
            return 0

    def perform(self):
        customer = self.model.objects.get(pk=self.r_id)
        query = {
            'limit': self.get_limit(),
            'offset': self.get_offset(),
            'source': { 'object': 'card' },
            'include[]': 'total_count'
        }

        if customer:
            query.customer = customer[self.user_field]

        charges = stripe.Charge.list(**query)
        for charge in charges:
            if customer:
                charge['data']['customer'] = customer
            else:
                query = { '%s' % self.user_field: r_id }
                customer = self.model.objects.filter(**query)
                charge['data']['customer'] = customer

        return [charges['total_count'], charges.data]
