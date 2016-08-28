from pydash import _
from serializer_utils import SerializerUtils


class Serializer(object):
    def __init__(self, collection_name, opts):
        self.payload = {}
        self.collection_name = collection_name
        self.opts = opts

    def serialize(self, records):
        if self.opts.get('top_level_links'):
            self.payload['links'] = \
            self._get_links(self.opts['top_level_links'], records)

        if self.opts.get('meta'):
            self.payload['meta'] = self.opts['meta']

        if _.is_list(records):
            return self._collection(records)
        else:
            return self._resource(records)

    def _get_links(self, links, records):
        def value_mapper(value):
            if _.is_function(value):
                return value(records)
            else:
                return value
        return _.map_values(links, value_mapper)

    def _collection(self, records):
        self.payload['data'] = []

        for rec in records:
            su = SerializerUtils(self.collection_name, rec, self.payload,
                                 self.opts)
            self.payload['data'].append(su.perform())

        return self.payload

    def _resource(self, records):
        self.payload['data'] = SerializerUtils(self.collection_name,
                                               records, self.payload,
                                               self.opts).perform()
        return self.payload
