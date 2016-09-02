from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from forest.services.stripe_payments_getter import StripePaymentsGetter
from forest.serializers.stripe import StripePaymentsSerializer

@csrf_exempt
def stripe_payments(request):
    getter = StripePaymentsGetter(request)
    data, count = getter.perform()
    json_api_data = StripePaymentsSerializer().serialize(data, count)
    return JsonResponse(json_api_data, safe=False)


@csrf_exempt
def stripe_refund(request):
    return HttpResponse(status=204)

@csrf_exempt
def stripe_invoices(request):
    return HttpResponse(status=204)

@csrf_exempt
def stripe_cards(request):
    return HttpResponse(status=204)


