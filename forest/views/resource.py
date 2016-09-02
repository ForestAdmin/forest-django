from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from forest.services.resource_getter import ResourceGetter
from forest.services.resource_updater import ResourceUpdater
from forest.services.resource_remover import ResourceRemover

from forest.services.utils import jwt_verify
from forest.serializers.resource import ResourceSerializer


@csrf_exempt
@jwt_verify
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

