from django.conf import settings
from django.db import models
from django.apps import apps

FIELDS_TYPE_MAPPING = {
    'AutoField': 'Number',
    'BigIntegerField': 'Number',
    'BinaryField': 'Number',
    'BooleanField': 'Boolean',
    'CharField': 'String',
    'CommaSeparatedIntegerField': 'String',
    'DateField': 'Date',
    'DateTimeField': 'Date',
    'DecimalField': 'Number',
    # TODO: not sure about DurationField
    # https://docs.djangoproject.com/en/1.9/ref/models/fields/#durationfield
    'DurationField': 'Number',
    'EmailField': 'String',
    # TODO: not sure about FileField
    # https://docs.djangoproject.com/en/1.9/ref/models/fields/#filefield
    'FileField': 'String',
    'FilePathField': 'String',
    'FloatField': 'Number',
    # TODO: not sure about ImageField
    # https://docs.djangoproject.com/en/1.9/ref/models/fields/#imagefield
    'ImageField': 'String',
    'IntegerField': 'Number',
    'GenericIPAddressField': 'String',
    # TODO: not sure about NullBooleanField
    # https://docs.djangoproject.com/en/1.9/ref/models/fields/#nullbooleanfield
    'NullBooleanField': 'Boolean',
    'PositiveIntegerField': 'Number',
    'PositiveSmallIntegerField': 'Number',
    'SlugField': 'String',
    'SmallIntegerField': 'Number',
    'TextField': 'String',
    'TimeField': 'Date',
    'URLField': 'String',
    'UUIDField': 'String',
}


class ApiMap():
    def __init__(self):
        self.apimap = {}

    def get(self):
        return self.apimap

    def get_models(self):
        for app in settings.INSTALLED_APPS:
            pass

    def generate(self):
        self.apimap = {
            'data': [],
            'meta': {
                'liana': 'forest-django',
                'liana_version': '0.0.1'
            }
        }
        models = apps.get_app_config(settings.FOREST_APP_MODELS).get_models()
        for model in models:
            data_item = {
                'id': model.__name__,
                'type': 'collections',
                'attributes': {},
                'links': {}
            }
            data_item['attributes']['name'] = model.__name__
            data_item['attributes']['fields'] = self.get_model_fields(model)
            data_item['attributes']['only-for-relationship'] = None
            data_item['attributes']['is-virtual'] = None
            data_item['attributes']['is-read-only'] = False
            data_item['attributes']['is-searchable'] = True

            data_item['links'] = {
                'self': '/collections/%s' % model.__name__
            }

            self.apimap['data'].append(data_item)

        return self.apimap

    def get_model_fields(self, model):
        fields = []
        for field in model._meta.get_fields():
            internal_type = field.get_internal_type()
            schema = {
                'field': field.name,
                'type': FIELDS_TYPE_MAPPING.get(internal_type, 'String')
            }
            if not field.is_relation:
                fields.append(schema)
            else:
                ref = field.related_model.__name__
                pk = field.related_model._meta.pk.name

                if field.one_to_many or field.many_to_many:
                    schema['field'] = ref
                    schema['type'] = ['Number']

                elif field.many_to_one:
                    ref = field.related_model.__name__

                schema['reference'] = "%s.%s" % (ref, pk)
                fields.append(schema)

        return fields

    def get_model_schema(self, model_name):
        schema = filter(lambda x: x['id'] == model_name, self.apimap['data'])
        if len(schema):
            return schema[0]

    def get_field_from_model(self, model_name, field_model):
        schema = self.get_model_schema(model_name)
        if schema is None:
            return
        for field in schema['attributes']['fields']:
            if field.get('reference', '').split('.')[0] == field_model:
                return field['field']

    def get_type(self, model_name, field_name):
        schema = self.get_model_schema(model_name)
        if schema is None:
            return

        for field in schema['attributes']['fields']:
            if field['field'] == field_name:
                return field['type']

api_map = ApiMap()
