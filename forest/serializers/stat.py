import uuid
from forest.serializers.serializer import Serializer as JSONApiSerializer

class StatSerializer():
    def serialize(self, stat):
        stat['id'] = uuid.uuid4()
        options = {
            'attributes': ['value'],
            'key_for_attribute': (lambda x: x)
        }
        ser = JSONApiSerializer('stat', options)
        return ser.serialize(stat)
