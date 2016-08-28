import jwt
from django.http import HttpResponse, JsonResponse
from django.apps import apps
from django.conf import settings


def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def get_model_class(model_name):
    models = apps.get_models()
    for model in models:
        if model.__name__.lower() == model_name.lower():
            return model

def jwt_get_user_id_from_payload_handler(payload):
    return payload.get('id')

#TODO: strenghten this
def jwt_verify(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        token = request.META['HTTP_AUTHORIZATION'].split()[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, True)
            return view_func(request, *args, **kwargs)
        except Exception as err:
            return HttpResponse(status=401)

    return _wrapped_view_func
