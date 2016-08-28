from django.apps import apps


class ResourceGetter():
    def __init__(self, request, model, r_id):
        self.request = request
        self.params = request.GET
        self.model_name = model
        self.model = self._get_model_class()
        self.r_id = r_id

    def _get_model_class(self):
        models = apps.get_models()
        for model in models:
            if model.__name__.lower() == self.model_name.lower():
                return model

    def perform(self):
        return self.model.objects.get(pk=self.r_id)
