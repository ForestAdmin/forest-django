import json
import dateutil.parser
from forest.services.utils import merge_dicts, get_model_class
from forest.generators import schemas


class ResourceRemover():
    def __init__(self, request, model_name, r_id):
        self.model = get_model_class(model_name)
        self.r_id = r_id

    def perform(self):
        item = self.model.objects.get(pk=self.r_id)
        item.delete()

