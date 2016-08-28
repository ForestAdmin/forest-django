import inflector
from pydash import _


class SerializerUtils(object):
    def __init__(self, collection_name, record, payload, opts):
        self.collection_name = collection_name
        self.record = record
        self.payload = payload
        self.opts = opts


    def key_for_attribute(self, attribute):
        def transform_callback(acc, value, key):
            if self._is_complex_type(value):
                acc[self.key_for_attribute(key)] = self.key_for_attribute(value)
            else:
                acc[self.key_for_attribute(key)] = value
            return acc, value, key

        def map_function(item):
            if self._is_complex_type(item):
                return self.key_for_attribute(item)
            else:
                return item

        if _.is_dict(attribute):
            return _.transform(attribute, transform_callback)


        elif _.is_list(attribute):
            map(map_function, attribute)

        else:
            if _.is_function(self.opts.get('key_for_attribute')):
                return opts[self.key_for_attribute(attribute)]
            else:
                caserized = inflector.caserize(attribute, self.opts)
                return caserized

    def get_id(self):
        return self.opts.get('id', 'id')

    def _is_complex_type(self, obj):
        return _.is_list(obj) or _.is_dict(obj)

    def get_ref(self, current, item, opts):
        if _.is_function(opts.get('ref')):
            return opts['ref'](current, item)
        elif opts.get('ref') is True:
            if _.is_list(item):
                return map(lambda val: str(val), item)
            elif item:
                return str(item)
        elif isinstance(item, dict) and item.get(opts.get('ref')):
            return str(item[opts['ref']])

    def get_type(self, string, attr_val):
        type_ = None
        attr_val = attr_val or {}
        if _.is_function(self.opts.get('type_for_attribute')):
            type_ = self.opts['type_for_attribute'](string, attr_val)

        if (self.opts.get('pluralize_type') is None or self.opts.get('pluralize_type')) and type_ is None:
            type_ = inflector.pluralize(string)

        if type_ is None:
            type_ = string

        return type_

    def get_links(self, current, links, dest):
        def map_function(item):
            if _.is_function(item):
                return item(self.record, current, dest)
            else:
                return item
        return _.map_values(links, map_function)

    def get_meta(self, current, meta):
        def map_function(item):
            if _.is_function(item):
                return item(self.record, current)
            else:
                return item

        return _.map_values(meta, map_function)

    def pick(self, obj, attributes):
        def map_function(value, key):
            return self.key_for_attribute(key)

        return _.map_keys(_.pick(obj, attributes), map_function)

    def is_compound_document_included(self, included, item):
        return _.find(self.payload.get('included', {}), {
            'id': item.get('id'),
            'type': item.get('type')
        })

    def push_to_included(self, dest, include):
        if not self.is_compound_document_included(dest, include):
            if not dest.get('included'):
                dest['included'] = []
            dest['included'].append(include)

    def serialize(self, dest, current, attribute, opts):
        data = None

        if opts and opts.get('ref'):
            if not dest.get('relationships'):
                dest['relationships'] = {}

            def map_current(item):
                return self.serialize_ref(item, current, attribute, opts)

            if _.is_list(current.get(attribute)):
                data = map(map_current, current[attribute])

            else:
                data = self.serialize_ref(current[attribute], current,
                                         attribute, opts)

            dest['relationships'][self.key_for_attribute(attribute)] = {}
            if not opts.get('ignore_relationship_data'):
                dest['relationships'][self.key_for_attribute(attribute)]['data'] = data

            if opts.get('relationship_links'):
                dest['relationships'][self.key_for_attribute(attribute)]['links'] = \
                    self.get_links(current[attribute], opts['relationship_links'], dest)

            if opts.get('relationship_meta'):
                dest['relationships'][self.key_for_attribute(attribute)]['meta'] = \
                    self.get_meta(current['attribute'], opts['relationship_meta'])
        else:
            if _.is_list(current[attribute]):
                if len(current[attribute]) and _.is_dict(current[attribute][0]):
                    def map_current(item):
                        return self.serialize_nested(item, current, attribute,
                                                    opts)
                    data = map(map_current, current[attribute])
                else:
                    data = current[attribute]

                dest['attributes'][self.key_for_attribute(attribute)] = data
            elif _.is_dict(current[attribute]):
                data = self.serialize_nested(current[attribute], current,
                                            attribute, opts)
                dest['attributes'][self.key_for_attribute(attribute)] = data
            else:
                dest['attributes'][self.key_for_attribute(attribute)] = current[attribute]

    def serialize_ref(self, dest, current, attribute, opts):
        id_ = self.get_ref(current, dest, opts)
        type_ = self.get_type(attribute, dest)

        relationships = []
        included_attrs = []

        if opts.get('attributes'):
            relationships = filter(lambda x: opts.get(x), opts['attributes'])
            included_attrs = filter(lambda x: opts.get(x) is None, opts['attributes'])

        included = { 'type': type_, 'id': id_ }
        if included_attrs:
            included['attributes'] = self.pick(dest, included_attrs)

        for rel in relationships:
            if self._is_complex_type(dest[rel]):
                self.serialize(included, dest, rel, opts[rel])

        if included_attrs and (opts.get('included') is None or
                               opts.get('included') is True):
            if opts.get('included_links'):
                included['links'] = self.get_links(dest, opts['included_links'])

            if id_ is not None:
                self.push_to_included(self.payload, included)

        if id_ is not None:
            return { 'type': type_, 'id': id_ }
        else:
            return None

    def serialize_nested(self, dest, current, attribute, opts):

        embeds = []
        attributes = []

        if opts and opts.get('attributes'):
            embeds = filter(lambda x: opts[x], opts['attributes'])
            attributes = filter(lambda x: opts[x] is None, opts['attributes'])
        else:
            attributes = _.keys(dest)

        ret = {}
        if attributes:
            ret['attributes'] = self.pick(dest, attributes)

        for embed in embeds:
            if self._is_complex_type(dest[embed]):
                self.serialize(ret, dest, embed, opts[embed])

        return ret['attributes']

    def perform(self):

        if self.record is None:
            return None

        data = {
            'type': self.get_type(self.collection_name, self.record),
            'id': str(self.record[self.get_id()])
        }

        if self.opts.get('data_links'):
            data['links'] = self.get_links(self.record, self.opts['data_links'], None)

        for attr in self.opts.get('attributes', []):
            splitted_attributes = attr.split(':')
            if len(splitted_attributes) and splitted_attributes[0] in self.record:
                if not data.get('attributes'):
                    data['attributes'] = {}

                attribute_map = attr;
                if len(splitted_attributes) > 1:
                    attr = splitted_attributes[0]
                    attribute_map = splitted_attributes[1]

                self.serialize(data, self.record, attr, self.opts.get(attribute_map))

        return data
