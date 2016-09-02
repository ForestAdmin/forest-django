from django.db import models
from forest.services import filter_generator
from forest.services import utils

def _get_aggregate(params):
    return getattr(models, params.get('aggregate', 'Count'))

def _get_group_by(params):
    return params.get('group_by_field')

def _get_filters(params):
    filters = []
    for item in params.get('filters', []):
        filters.append(filter_generator.get(item['field'], item['value']))

    all_filters = utils.merge_dicts(*filters)
    return all_filters

def perform(params, model_name):
    model = utils.get_model_class(model_name)
    group_by_field = _get_group_by(params)
    aggregate = _get_aggregate(params)
    filters = _get_filters(params)
    query = model.objects
    query = query.filter(**filters)
    query = query.values(group_by_field)
    query = query.annotate(value=aggregate(group_by_field))

    # The following cast to list is necessary to override the "remaining
    # elements truncated" limitation of django queryset result. Maybe there's a
    # better way.
    # TODO: Should we set a limit? Would make sense for pie charts.

    data = list(query.order_by('-value'))
    for item in data:
        item['key'] = item.pop(group_by_field)

    return { 'value': data }

