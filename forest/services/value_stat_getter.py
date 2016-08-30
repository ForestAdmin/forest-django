from django.db import models
from forest.services import filter_generator
from forest.services import utils

def _get_aggregate(params):
    return getattr(models, params.get('aggregate', 'Count'))

def _get_aggregate_field(params):
    return params.get('aggregate_field') or 'id'

def _get_filters(params):
    filters = []

    for k,v in params.iteritems():
        if k.startswith('filter['):
            match = re.match(r'filter\[(.*)\]', k)
            if match:
                filter_field = match.group(1)
                filters.append(filter_generator.get(filter_field, v))

    all_filters = utils.merge_dicts(*filters)
    return all_filters


def perform(params, model_name):
    model = utils.get_model_class(model_name)
    aggregate_field = _get_aggregate_field(params)
    aggregate = _get_aggregate(params)
    filters = _get_filters(params)
    data = model.objects.aggregate(aggregate(aggregate_field))
    generated_field = "%s__%s" % (aggregate_field, params.get('aggregate').lower())
    count = data[generated_field]
    return {
        'value': {
            'countCurrent': count
        }
    }

