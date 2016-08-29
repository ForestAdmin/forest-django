import bcrypt
import jwt
import datetime
import json

from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from django.apps import apps

from forest.services.allowed_user_getter import get_allowed_users

from forest.services.resources_getter import ResourcesGetter
from forest.services.resource_getter import ResourceGetter
from forest.services.resource_creator import ResourceCreator
from forest.services.resource_updater import ResourceUpdater
from forest.services.resource_remover import ResourceRemover

from forest.serializers.serializer import Serializer
from forest.serializers.resource import ResourceSerializer
from forest.serializers.stripe import StripePaymentsSerializer

@csrf_exempt
def empty(request):
    return HttpResponse()

def passwords_match(plain, hashed):
    return bcrypt.hashpw(str(plain), str(hashed)) == str(hashed)

@csrf_exempt
def session(request):
    data = json.loads(request.body)
    allowedUsers = get_allowed_users(data.get('renderingId'))
    user = (u for u in allowedUsers if u['email'] == data['email']).next()
    if len(user) and passwords_match(data['password'], user['password']):
        payload = {
            'id': user['id'],
            'type': 'users',
            'data': {
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'teams': user['teams']
            },
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14)
        }

        print settings.JWT_SECRET_KEY
        secret_key = settings.JWT_SECRET_KEY
        token = jwt.encode(payload, secret_key)
        return JsonResponse({ 'token': token })

    else:
        return HttpResponse(status=401)


def get_model_class(model_name):
    models = apps.get_models()
    for model in models:
        if model.__name__.lower() == model_name.lower():
            return model


from forest.services.utils import jwt_verify
@csrf_exempt
def resources(request, model):
    json_api_data = {}

    if request.method == 'GET':
        getter = ResourcesGetter(request, model)
        data = getter.perform()
        count = getter.count
        json_api_data = ResourceSerializer(model).serialize(data, count)
    elif request.method == 'POST':
        creator = ResourceCreator(request, model)
        data = creator.perform()
        json_api_data = ResourceSerializer(model).serialize([data,], 1, single=True)

    return JsonResponse(json_api_data, safe=False)


# class Resources(JSONWebTokenAuthMixin, View):
    # def get(self, request, model):
        # getter = ResourcesGetter(request, model)
        # data = getter.perform()
        # count = getter.count
        # json_api_data = ResourceSerializer(model).serialize(data, count)
        # return JsonResponse(json_api_data, safe=False)

    # def post(self, request, model):
        # creator = ResourceCreator(request, model)
        # data = creator.perform()
        # json_api_data = ResourceSerializer(model).serialize([data,], 1, single=True)
        # return JsonResponse(json_api_data, safe=False)

@csrf_exempt
def resource(request, model, r_id):
    json_api_data = {}
    if request.method == 'GET':
        getter = ResourceGetter(request, model, r_id)
        data = getter.perform()
        json_api_data = ResourceSerializer(model).serialize([data,], 1, single=True)
    elif request.method == 'PUT':
        updater = ResourceUpdater(request, model, r_id)
        data = updater.perform()
        json_api_data = ResourceSerializer(model).serialize([data,], 1, single=True)

    elif request.method == 'DELETE':
        remover = ResourceRemover(request, model, r_id)
        remover.perform()
        return HttpResponse(status=204)

    return JsonResponse(json_api_data, safe=False)

@csrf_exempt
def association(request, model, r_id, association):
    getter = ResourcesGetter(request, model, r_id, association=association)
    data = getter.perform()
    json_api_data = ResourceSerializer(model).serialize([data,], 1)

    return JsonResponse(json_api_data, safe=False)


@csrf_exempt
def stripe_payments(request):
    getter = StripePaymentsGetter(request)
    data, count = getter.perform()
    json_api_data = StripePaymentsSerializer().serialize(data, count)
    return JsonResponse(json_api_data, safe=False)

@csrf_exempt
def stripe_refund(request):
    pass

@csrf_exempt
def stripe_invoices(request):
    pass

@csrf_exempt
def stripe_cards(request):
    pass
