import re
from operator import __or__ as OR

from django.db.models import ForeignKey
from django.db.models import Q

from forest.services import filter_generator
from forest.services import utils
from forest.generators import schemas


def _handle_limit(params):
    if params.get('page[size]'):
        return int(params['page[size]'])
    return 10

def _handle_offset(params, limit):
    if params.get('page[number]'):
        return (int(params['page[number]']) - 1) * limit
    return 0

def _handle_sort(params):
    if params.get('sort'):
        return params['sort'].replace('.', '__')

def _get_q_filter_key(model_name, association):
    model = utils.get_model_class(association)
    fields = model._meta.get_fields()
    for field in fields:
        if field.is_relation and field.related_model.__name__ == model_name:
            return field.name

def perform(request, model_name, r_id, association):
    model = utils.get_model_class(association)
    filter_key = _get_q_filter_key(model_name, association)
    q_filter = { '%s' % filter_key: r_id }
    #TODO: is this useful?
    related_fields = [f.name for f in model._meta.get_fields() if isinstance(f, ForeignKey)]
    params = request.GET
    limit = _handle_limit(params)
    offset = _handle_offset(params, limit)
    sort = _handle_sort(params)
    query = model.objects.select_related(*related_fields).filter(**q_filter)
    count = query.count()
    if sort:
        query = query.order_by(sort)

    return query[offset:offset+limit], count
