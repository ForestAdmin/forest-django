import jwt
import bcrypt
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

def passwords_match(plain, hashed):
    return bcrypt.hashpw(str(plain), str(hashed)) == str(hashed)

def jwt_get_user_id_from_payload_handler(payload):
    return payload.get('id')

def jwt_verify(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if hasattr(request, 'META') and request.META.get('HTTP_AUTHORIZATION'):
            splitted_token = request.META['HTTP_AUTHORIZATION'].split()
            if len(splitted_token):
                token = splitted_token[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, True)
            return view_func(request, *args, **kwargs)
        except jwt.DecodeError as err:
            return HttpResponse(status=401)

    return _wrapped_view_func
