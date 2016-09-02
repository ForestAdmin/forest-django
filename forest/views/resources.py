from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from forest.services.utils import jwt_verify
from forest.services.resources_getter import ResourcesGetter
from forest.services.resource_creator import ResourceCreator
from forest.serializers.resource import ResourceSerializer


@csrf_exempt
@jwt_verify
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

