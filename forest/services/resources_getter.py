import re
from operator import __or__ as OR

from django.db.models import ForeignKey
from django.db.models import Q

from forest.services import filter_generator
from forest.services import utils


class ResourcesGetter():
    def __init__(self, request, model, r_id=None, association=None):
        self.request = request
        self.params = request.GET
        self.model = utils.get_model_class(model)
        self.count = 0
        self.r_id = r_id
        self.association = association

    def _get_limit(self):
        if self.params.get('page[size]'):
            return int(self.params['page[size]'])
        return 10

    def _get_offset(self):
        if self.params.get('page[number]'):
            return (int(self.params['page[number]']) - 1) * self._get_limit()
        return 0

    def _get_sort(self):
        if self.params.get('sort'):
            return self.params['sort'].replace('.', '__')

    def _handle_search_param(self, params):
        pass

    def is_filter_field_valid(self, field):
        return field in self.model._meta.get_all_field_names()

    def _merge_dicts(self, *dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def _handle_filter_param(self):
        filters = []

        for k,v in self.params.iteritems():
            if k.startswith('filter['):
                match = re.match(r'filter\[(.*)\]', k)
                if match:
                    filter_field = match.group(1)
                    if self.is_filter_field_valid(filter_field):
                        filters.append(filter_generator.get(filter_field, v))

        all_filters = self._merge_dicts(*filters)
        return all_filters

    def _handle_search_param(self):
        search_param = self.params.get('search')
        if not search_param:
            return

        fields = [f.name for f in self.model._meta.get_fields() if not f.is_relation]
        q_list = [Q(**{'%s__icontains' % f : search_param}) for f in fields]
        related = [f for f in self.model._meta.get_fields() if isinstance(f, ForeignKey)]
        for rel in related:
            model = rel.related_model
            r_fields = [f.name for f in model._meta.get_fields() if not f.is_relation]
            q_list += [Q(**{'%s__%s__icontains' % (rel.name, r_field): search_param}) for r_field in r_fields]
        search_filter = reduce(OR, q_list)

        return search_filter

    def _get_related_fields(self):
        return [f.name for f in self.model._meta.get_fields() if isinstance(f, ForeignKey)]

    def _build_query(self):
        related_fields = self._get_related_fields()
        sort = self._get_sort()
        filters = self._handle_filter_param()
        search_filter = self._handle_search_param()

        query = self.model.objects
        if filters:
            query = query.filter(**filters)
        elif search_filter:
            query = query.filter(search_filter)
        if sort:
            query = query.order_by(sort)
        if related_fields:
            query = query.select_related(*related_fields)

        return query


    def perform(self):
        self.count = self._build_query().count()

        offset = self._get_offset()
        limit = self._get_limit()
        data = self._build_query()[offset:offset+limit]
        return data
