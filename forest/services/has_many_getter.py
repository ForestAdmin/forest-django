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
    print "Model: %s; association: %s" % (model_name, association)
    model = utils.get_model_class(association)
    fields = model._meta.get_fields()
    for field in fields:
        print "Dealing with: %s" % field
        # if field.name == 'actors':
            # import pdb; pdb.set_trace()
        if field.is_relation and field.many_to_many:
            if hasattr(field, 'rel'):
                if field.rel.to.__name__ == model_name:
                    return field.name
            else:
                if field.related_model.__name__ == model_name:
                    return field.name
        if field.is_relation and isinstance(field, ForeignKey):
            if field.rel.to.__name__ == model_name:
                return field.name


def perform(request, model_name, r_id, association):
    model = utils.get_model_class(association)
    filter_key = _get_q_filter_key(model_name, association)
    q_filter = { '%s' % filter_key: r_id }
    print "Filter key: %s" % filter_key
    related_fields = [f.name for f in model._meta.get_fields() if isinstance(f, ForeignKey)]
    params = request.GET
    limit = _handle_limit(params)
    offset = _handle_offset(params, limit)
    sort = _handle_sort(params)
    query = model.objects.select_related(*related_fields).filter(**q_filter)
    if sort:
        query = query.order_by(sort)
    return query[offset:offset+limit]
