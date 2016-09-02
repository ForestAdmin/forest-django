from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from forest.services.utils import jwt_verify
from forest.services import has_many_getter
from forest.serializers.resource import ResourceSerializer


@csrf_exempt
@jwt_verify
def association(request, model, r_id, association):
    data, count = has_many_getter.perform(request, model, r_id, association)
    json_api_data = ResourceSerializer(association).serialize(data, count)
    return JsonResponse(json_api_data, safe=False)
