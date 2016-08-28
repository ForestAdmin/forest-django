import json

from django.core import serializers
from django.db.models import ForeignKey

from django.apps import apps
from forest.generators import schemas
from forest.serializers.serializer import Serializer as JSONApiSerializer


class ResourceSerializer():
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = self.get_model_class(model_name)
        self.api_map = schemas.api_map.get()

    def _get_attributes(self):
        attributes = []
        for schema in self.api_map['data']:
            if schema['id'] == self.model_name:
                attributes = schema['attributes']
        return attributes

    def _get_fields(self, attributes):
        return (x for x in attributes['fields'])

    def _fct_wrapper(self, field):
        """
        The relationship_links_fct function cannot be a closure, as the nested
        function looks up variables from the parent scope when executed,
        not when defined. It would therefore lose the "field" reference.
        """
        def relationship_links_fct(record, current, parent):
            return {
                'href': '/forest/%s/%s/%s' % (self.model_name, parent['id'],
                                              field)
            }
        return relationship_links_fct

    def _get_related_fields(self):
        return [f.name for f in self.model._meta.get_fields() if isinstance(f, ForeignKey)]

    def _get_model_fields(self, model_name):
        for model in self.api_map['data']:
            if model['id'] == model_name:
                return [f['field'] for f in model['attributes']['fields']]

    def _get_options(self, queryset):
        attributes = self._get_attributes()
        fields = [x['field'] for x in attributes['fields']]
        options = { 'attributes': fields, 'key_for_attribute': 'snake_case' }
        related_fields = self._get_related_fields()

        for field in self._get_fields(attributes):
            included = field['field'].lower() in related_fields
            if field.get('reference'):
                options[field['field']] = { 'ref': 'id' }
                if not included:
                    options[field['field']]['included'] = False
                    options[field['field']]['ignore_relationship_data'] = True
                    options[field['field']]['relationship_links'] = {
                        'related': self._fct_wrapper(field['field'])
                    }
                else:
                    related_model = field['reference'].split('.')[0]
                    options[field['field']]['attributes'] = self._get_model_fields(related_model)
                    options[field['field']]['relationship_links'] = {
                        'related': self._fct_wrapper(related_model)
                    }


        return options

    def _format_records(self, queryset):
        attributes = self._get_attributes()
        attr_fields = [x['field'] for x in attributes['fields']]
        related_fields = self._get_related_fields()
        json_data = serializers.serialize('json', queryset)
        records = json.loads(json_data)

        data = []
        for index, rec in enumerate(records):
            rec['fields']['id'] = rec['pk']
            for field in attr_fields:
                if field not in rec['fields']:
                    rec['fields'][field] = []
            for field in related_fields:
                rel_obj = getattr(queryset[index], field)
                ser_rel_obj = serializers.serialize('json', [rel_obj,])
                rel_data = json.loads(ser_rel_obj)[0]
                rel_data['fields']['id'] = rel_data['pk']
                rec['fields'][field] = rel_data['fields']
            data.append(rec['fields'])

        return data

    def get_model_class(self, model_name):
        models = apps.get_models()
        for model in models:
            if model.__name__.lower() == model_name.lower():
                return model

    def _set_meta(self, options, count):
        options['meta'] = { 'count': count }
        return options

    def serialize(self, queryset, count, single=False):
        name = self.model_name
        options = self._get_options(queryset)
        if not single:
            options = self._set_meta(options, count)
        resource_serializer = JSONApiSerializer(name, options)
        formatted_records = self._format_records(queryset)
        if single:
            formatted_records = formatted_records[0]
        return resource_serializer.serialize(formatted_records)

