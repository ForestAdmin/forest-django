import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from forest.services.utils import jwt_verify
from forest.services import value_stat_getter
from forest.services import pie_stat_getter
from forest.services import line_stat_getter
from forest.serializers.stat import StatSerializer


@csrf_exempt
def stat(request, model):
    if request.method == 'POST':
        payload = json.loads(request.body)
        if payload.get('type') == 'Value':
            data = value_stat_getter.perform(payload, model)
            json_api_data = StatSerializer().serialize(data)
            return JsonResponse(json_api_data, safe=False)
        elif payload.get('type') == 'Pie':
            data = pie_stat_getter.perform(payload, model)
            json_api_data = StatSerializer().serialize(data)
            return JsonResponse(json_api_data, safe=False)
        elif payload.get('type') == 'Line':
            data = line_stat_getter.perform(payload, model)
            json_api_data = StatSerializer().serialize(data)
            return JsonResponse(json_api_data, safe=False)

    return HttpResponse(status=204)
