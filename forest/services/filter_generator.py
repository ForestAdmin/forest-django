from django.db.models import Q
from django.db.models import Lookup
from django.db.models.fields import Field

from forest.services import operator_date_interval_parser as date_parser

class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

Field.register_lookup(NotEqual)

def get(field_name, value):

    if not len(value):
        return

    if value[0] == '!':
        value = value[1:]
        return {"%s__ne" % field_name: value}

    elif value[0] == '<':
        value = value[1:]

        if date_parser.is_interval_date_value(value):
            start, end = date_parser.get_interval_date_filter(value)
            return {"%s__range" % field_name: [start, end]}

        return {"%s__lt" % field_name: value}

    elif value[0] == '>':
        value = value[1:]

        if date_parser.is_interval_date_value(value):
            start, end = date_parser.get_interval_date_filter(value)
            return {"%s__range" % field_name: [start, end]}

        return {"%s__gt" % field_name: value}

    elif value[0] == '*' and value[-1] == '*':
        value = value[1:-1]
        return {"%s__icontains" % field_name: value}

    elif value[0] == '*':
        value = value[1:]
        return {"%s__endswith" % field_name: value}

    elif value[-1] == '*':
        value = value[:-1]
        return {"%s__starswith" % field_name: value}

    elif value == '$present':
        return {"%s__isnull" % field_name: False}

    elif value == '$blank':
        return {"%s__isnull" % field_name: True}

    else:
        return {field_name: value}


