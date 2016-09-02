import jwt
import json
import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from forest.services.allowed_user_getter import get_allowed_users
from forest.services.utils import passwords_match

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

        secret_key = settings.JWT_SECRET_KEY
        token = jwt.encode(payload, secret_key)
        return JsonResponse({ 'token': token })

    else:
        return HttpResponse(status=401)

