import importlib
import pkgutil
from django.conf import settings
from django.db import models
from django.apps import apps
from forest.serializers.serializer import Serializer as JSONApiSerializer

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
        self.actions = []
        self.init_actions()
        self.smart_collections = []
        self.init_smart_collections()

    def get(self):
        return self.apimap

    def get_models(self):
        for app in settings.INSTALLED_APPS:
            pass

    def generate(self):
        data = []
        models = apps.get_app_config(settings.FOREST_APP_NAME).get_models()
        for model in models:
            data.append(self.get_schema(model))

        data += self.smart_collections
        self.apimap = self.serialize(data)
        return self.apimap

    def init_actions(self):
        """Imports actions from FOREST_APP_NAME/forest/actions folder. This
        does not import recursively.
        """
        mod_path = "%s.forest.actions" % settings.FOREST_APP_NAME
        try:
            actions_module = importlib.import_module(mod_path)
            for loader, name, ispkg in pkgutil.iter_modules(actions_module.__path__):
                action_module = loader.find_module(name).load_module(name)
                if hasattr(action_module, 'ACTION'):
                    self.actions.append(action_module.ACTION)
        except ImportError as err:
            pass

    def init_smart_collections(self):
        """Imports actions from FOREST_APP_NAME/forest/smart_collections
        folder. This does not import recursively.
        """
        mod_path = "%s.forest.smart_collections" % settings.FOREST_APP_NAME
        try:
            sc_module = importlib.import_module(mod_path)
            for loader, name, ispkg in pkgutil.iter_modules(sc_module.__path__):
                sc_module = loader.find_module(name).load_module(name)
                if hasattr(sc_module, 'SMART_COLLECTION'):
                    self.smart_collections.append(sc_module.SMART_COLLECTION)
        except ImportError as err:
            pass

    def get_actions(self, model_name):
        actions = []
        for action in self.actions:
            if action.get('collection') == model_name:
                actions.append(action)
        return actions

    def get_schema(self, model):
        schema = {
            'name': model.__name__,
            'fields': self.get_model_fields(model),
            'only-for-relationship': None,
            'is-virtual': None,
            'is-read-only': False,
            'is-searchable': True,
            'actions': self.get_actions(model.__name__)
        }
        return schema

    def serialize(self, apimap):
        options = {
            'id': 'name',
            'attributes': ['name', 'displayName', 'paginationType', 'icon',
                           'fields', 'actions', 'onlyForRelationships',
                           'isVirtual', 'isReadOnly'],
            'fields': {
                'attributes': ['field', 'displayName', 'type', 'enums',
                               'collection_name', 'reference', 'column',
                               'isSearchable', 'widget', 'integration']
            },
            'actions': {
                'ref': 'name',
                'attributes': ['name', 'endpoint', 'httpMethod', 'fields']
            },
            'meta': {
                'liana': 'forest-django',
                'liana_version': '0.0.1'
            }
        }
        ser = JSONApiSerializer('collections', options)
        ser_apimap = ser.serialize(apimap)
        return ser_apimap

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
